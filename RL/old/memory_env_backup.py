import gym
import subprocess
import numpy as np
from numpy import dtype


class Memory_v0 (gym.Env):
    # Actions
    #   Flags that are verified with ../Preprocess/Flag_Seive.sh
    #   Use FLAG_NUM flags
    #   Flag lists are stored in ../Preprocess/Valid_Flags.txt
    #
    # States
    #   States are feature obtained from PCA in ../Preprocess/Faeture_PCA.py
    #   States info are stored in ../Preprocess/Feature_PCA_Result.txt
    #

    NEG_INF = -1e8

    def get_preprocess_values(self):
        with open("../Preprocess/Valid_Flags.txt", "r") as f:
            self.TOTAL_FLAG_NUM = int(f.readline().strip())
            self.FLAG_LIST = list()
            for _ in range(self.TOTAL_FLAG_NUM):
                s = f.readline().strip()
                self.FLAG_LIST.append(s)
            print("# Valid Flags: ", self.TOTAL_FLAG_NUM)
            print("Flag lists: ", self.FLAG_LIST)
        with open("../Preprocess/Feature_PCA_Result.txt", "r") as f:
            self.FEATURE_NUM = int(f.readline().strip())


    def get_feature(self):
        # Run LLVM Pass feature extraction
        feature_file = "./data/feature_" + self.ir.split('.')[0] + ".in"
        subprocess.run(["bash", "feature_extract.sh", self.tmp_ir, feature_file])

        # Apply PCA to obtained feature
        subprocess.run(["python3", "Feature_PCA.py", feature_file])
        feature = list()
        with open("./data/feature.in", "r") as f:
            self.FEATURE_NUM = int(f.readline().strip())
            for _ in range(self.FEATURE_NUM):
                feat = float(f.readline().strip())
                feature.append(feat)
        return feature


    def get_performance(self, ir, flag):
        process = subprocess.Popen(["bash", "compile_and_profile.sh", ir, flag], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        performance = int(process.communicate()[0])
        errmsg = str(process.communicate()[1])
        if errmsg != "":
            print("    ! (COMPILE_AND_PROFILE.SH ERR)  ERRMSG: ", errmsg)
        return performance


    def get_reward (self, action):
        performance = self.get_performance(self.tmp_ir, self.FLAG_LIST[action])
        reward = performance - self.prev_performance
        self.prev_performance = performance
        return reward


    metadata = { "render.modes": ["human"] }

    def __init__ (self):
        # Currently using irfile
        self.ir = "target.bc"
        self.tmp_ir = "./tmp/" + self.ir # IR used while training RL (kepp changing)
        self.data_ir = "./data/" + self.ir # Original IR (constant)

        # Initialize working ir file
        subprocess.run(["rm", "-f", self.tmp_ir])
        subprocess.run(["cp", self.data_ir, self.tmp_ir])

        # Initial values from preprocessing
        self.get_preprocess_values()
        self.FLAG_NUM = self.TOTAL_FLAG_NUM

        # Action space is flags
        #   Value is the index of the FLAG_LIST
        self.action_space = gym.spaces.Discrete(self.TOTAL_FLAG_NUM)

        # Observation space is number of features
        #   Box is consists of 2 parts
        #       1. 0 ~ FLAG_NUM-1: histogram of used flags
        #       2. FLAG_NUM ~ FLAG_NUM+FEATURE_NUM-1: values for each features
        self.observation_space = gym.spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(self.FLAG_NUM+self.FEATURE_NUM, ),
            dtype=np.float32)
        
        # Action history
        self.action_history = [0] * self.FLAG_NUM

        self.reset()


    def reset (self):
        """
        Reset the state of the environment and returns an initial observation.

        Returns
        -------
        observation (object): the initial observation of the space.
        """
        self.action_history = [0] * self.FLAG_NUM
        self.feature = self.get_feature()

        # State is history + feature
        self.state = np.array(self.action_history + self.feature, 
            dtype=np.float32)
        self.reward = 0
        self.done = False
        self.info = {}

        # Initialize working ir file
        subprocess.run(["rm", "-f", self.tmp_ir])
        subprocess.run(["cp", self.data_ir, self.tmp_ir])

        # Get baseline performance
        self.prev_performance = self.get_performance(self.tmp_ir, "-no-flag")

        return self.state
    

    def step (self, action):
        """
        The agent takes a step in the environment.
        """
        if self.done:
            # code should never reach this point
            print("EPISODE DONE!!!")
        
        elif self.action_history == [1] * self.FLAG_NUM:
            # Every flag is used
            self.done = True

        elif self.action_history[action] == 1:
            self.reward = self.NEG_INF
            self.done = True

        else:
            assert self.action_space.contains(action)

            self.action_history[action] += 1
            self.state = np.array(self.action_history + self.feature, 
                dtype=np.float32)
            self.reward = self.get_reward(action)

        try:
            assert self.observation_space.contains(self.state)
        except AssertionError:
            print("INVALID STATE", self.state)

        return [self.state, self.reward, self.done, self.info]


    def render (self, mode="human"):
        """Renders the environment.
        """
        s = "position: {}  reward: {}  info: {}"
        print(s.format(self.state, self.reward, self.info))


    def close (self):
        pass