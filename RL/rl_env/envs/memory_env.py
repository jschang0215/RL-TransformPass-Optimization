from pickle import FALSE
import gym
import subprocess
import numpy as np
import random
import os
from numpy import dtype
import datetime

DEBUG = False

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

    def print_action(self, action):
        print("Current action: ", end="")
        for flag_idx in action:
            print(self.FLAG_LIST[flag_idx], end=" | ")
        print("")


    def print_feature(self):
        print("Current feature: ", end="")
        for pca_idx in range(len(self.feature)):
            print(str(round(self.feature[pca_idx], 3)), end=" ")
        print("")


    def get_preprocess_values(self):
        with open("../Preprocess/Valid_Flags.txt", "r") as f:
            self.TOTAL_FLAG_NUM = int(f.readline().strip())
            self.FLAG_LIST = list()
            for _ in range(self.TOTAL_FLAG_NUM):
                s = f.readline().strip()
                self.FLAG_LIST.append(s)

            if DEBUG:
                print("# Valid Flags: ", self.TOTAL_FLAG_NUM)
                print("Flag lists: ", self.FLAG_LIST)
        with open("../Preprocess/Feature_PCA_Result.txt", "r") as f:
            self.FEATURE_NUM = int(f.readline().strip())


    def get_feature(self):
        # Run LLVM Pass feature extraction
        self.feature_raw_file = self.data_path + "feature_" + self.ir.split('.')[0] + "_raw.in"
        self.feature_pca_file = self.data_path + "feature_" + self.ir.split('.')[0] + "_pca.in"
        subprocess.run(["bash", "feature_extract.sh", self.tmp_ir, self.feature_raw_file])

        # Apply PCA to obtained feature
        subprocess.run(["python3", "Feature_PCA.py", self.feature_raw_file, self.feature_pca_file])
        feature = list()
        with open(self.feature_pca_file, "r") as f:
            self.FEATURE_NUM = int(f.readline().strip())
            for _ in range(self.FEATURE_NUM):
                feat = float(f.readline().strip())
                feature.append(feat)
        subprocess.run(["rm", self.feature_raw_file])
        subprocess.run(["rm", self.feature_pca_file])
        return feature


    def get_performance(self, ir, flags):
        retry_num = 0
        while True: # repeat until no error
            process = subprocess.Popen(["bash", "compile_and_profile.sh", ir, flags], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if retry_num >= 2:
                print(process.communicate())

            if process.communicate()[0] == '': 
                retry_num += 1
                print("Retrying get_performance: ", retry_num)
                if retry_num > 10: return self.base_performance
                continue
            performance = int(process.communicate()[0])
            errmsg = str(process.communicate()[1])
            if errmsg != "":
                print("    ! (COMPILE_AND_PROFILE.SH ERR)  ERRMSG: ", errmsg)
            break
        return performance


    def get_reward (self, action):
        process = subprocess.Popen(["stat", "-c%s", self.data_ir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if self.base_ir_size != int(process.communicate()[0]):
            print("Update base")
            # self.base_performance = self.get_performance(self.data_ir, "-no-flag")
            self.base_performance = self.get_performance(self.data_ir, "-o0")

        flags = ""
        for flag_idx in action:
            flags += (self.FLAG_LIST[flag_idx] + " ")
        performance = self.get_performance(self.tmp_ir, flags.strip())
        diff = performance - self.base_performance # low memory usage is good
        percent = (diff / self.base_performance)*100
        print("Memory Usage: ", round(percent, 3), "% (neg is good)")
        reward = - percent * 100
        return reward # performance improvement is good


    metadata = { "render.modes": ["human"] }

    def __init__ (self):

        # Currently using irfile move to workspace
        path_prefix = "env_" + str(random.randint(0, 1000000)) + "/" # File should be seperated for multi-core
        self.ir = "target.bc"
        self.tmp_path = "./tmp/" + path_prefix
        self.data_path = "./data/" + path_prefix
        subprocess.run(["mkdir", self.tmp_path])
        subprocess.run(["mkdir", self.data_path])
        self.tmp_ir = "./tmp/" + path_prefix + self.ir # IR used while training RL (kepp changing)
        self.data_ir = "./data/" + path_prefix + self.ir # Original IR (constant)
        subprocess.run(["cp", "./data/target.bc", self.data_ir])
        subprocess.run(["cp", "./data/target.bc", self.tmp_ir])
        # subprocess.run(["rm", "./data/target.bc"])

        # Initial values from preprocessing
        self.get_preprocess_values()
        self.used_flag_num = 12

        # Action space is flags
        #   Value is the index of the FLAG_LIST
        self.action_space = gym.spaces.Box(
            low=0, 
            high=(self.TOTAL_FLAG_NUM-1), 
            shape=(self.used_flag_num, ), 
            dtype=np.int32)

        # Observation space is number of features
        #   Box is consists of 2 parts
        #       1. 0 ~ FLAG_NUM-1: histogram of used flags
        #       2. FLAG_NUM ~ FLAG_NUM+FEATURE_NUM-1: values for each features
        self.observation_space = gym.spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(self.FEATURE_NUM, ),
            dtype=np.float32)

        self.reset()


    def reset (self):
        """
        Reset the state of the environment and returns an initial observation.

        Returns
        -------
        observation (object): the initial observation of the space.
        """
        self.feature = self.get_feature()

        # State is history + feature
        self.state = np.array(self.feature, 
            dtype=np.float32)
        self.reward = 0
        self.done = False
        self.info = {}

        # Initialize working ir file
        subprocess.run(["cp", "./data/target.bc", self.data_ir])
        subprocess.run(["cp", "./data/target.bc", self.tmp_ir])

        # Get baseline performance
        self.base_performance = self.get_performance(self.data_ir, "-no-flag")
        
        # Episode index (used for when to initialize ir and base performance)
        process = subprocess.Popen(["stat", "-c%s", self.data_ir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.base_ir_size = int(process.communicate()[0])

        self.epsidoe_idx = 0

        return self.state
    

    def step (self, action):
        """
        The agent takes a step in the environment.
        """

        if DEBUG:
            self.print_feature()
            self.print_action(action)

        if self.done:
            # code should never reach this point
            print("EPISODE DONE!!!")

        else:
            assert self.action_space.contains(action)

            self.state = np.array(self.feature, 
                dtype=np.float32)
            self.reward = self.get_reward(action)
            self.done = True

            
            # Clear unused workspace
            tmp_dir_lists = os.listdir("./tmp")
            for tmp_dir in tmp_dir_lists:  # Empty tmp folders are done folder
                path = "./tmp/" + tmp_dir + "/"
                try:
                    file_modified = datetime.fromtimestamp(os.path.getmtime(path))
                except:
                    file_modified = datetime.datetime.now()
                if datetime.datetime.now() - file_modified > datetime.timedelta(seconds=30):
                    print("Delete ", path)
                    try:
                        os.rmdir(path)
                    except:
                        pass


            # subprocess.run(["rm", "-r", self.data_path])
            # subprocess.run(["rm", "-r", self.tmp_path])
            

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