#!/usr/bin/env python
from email.mime import base
from rl_env.envs.memory_env import Memory_v0
from ray.tune.registry import register_env
import subprocess
import os
import ray
import ray.rllib.agents.ppo as ppo
import ray.rllib.agents.a3c as a3c
import ray.rllib.agents.es as es
import ray.rllib.agents.pg as pg
import datetime
import random
import statistics
import csv

RL_ALGORITHM = "PPO"
DEBUG = True
BASE_FLAG = "-Os"

CLUSTER_NUM = 4
INITIAL_CLUSTER_IDX = 0
IR_DIRECTORY_BASE_PATH="../Preprocess/clustered_ir/cluster_"
IR_DIRECTORY_PATH="../Preprocess/clustered_ir/cluster_" + str(INITIAL_CLUSTER_IDX) + "/"
CHK_PATH = "./checkpoints/08-16-PPO-Action12-Flag32/checkpoint-302"

class RL_Test ():

    def print_action(self, action):
        print("Current action: ", end="")
        for flag_idx in action:
            print(self.FLAG_LIST[flag_idx], end=" | ")
        print("")


    def print_feature(self):
        print("Current feature: ", end="")
        for pca_idx in range(len(self.feature)):
            print(str(pca_idx), ": ", str(round(self.feature[pca_idx], 3)), end=" | ")
        print("")

    def get_preprocess_values(self):
        with open("../Preprocess/Valid_Flags.txt", "r") as f:
            self.TOTAL_FLAG_NUM = int(f.readline().strip())
            self.FLAG_LIST = list()
            for _ in range(self.TOTAL_FLAG_NUM):
                s = f.readline().strip()
                self.FLAG_LIST.append(s)
        with open("../Preprocess/Feature_PCA_Result.txt", "r") as f:
            self.FEATURE_NUM = int(f.readline().strip())

    def initialize_ir(self, ir):
        original_path = ir
        new_path = "./data/target.bc"
        subprocess.run(["cp", original_path, new_path])
        path_prefix = "test_" + str(random.randint(0, 1000000)) + "/" # File should be seperated for multi-core
        self.ir = "target.bc"
        self.tmp_path = "./tmp/" + path_prefix
        self.data_path = "./data/" + path_prefix
        subprocess.run(["mkdir", self.tmp_path])
        subprocess.run(["mkdir", self.data_path])
        self.tmp_ir = "./tmp/" + path_prefix + self.ir # IR used while training RL (kepp changing)
        self.data_ir = "./data/" + path_prefix + self.ir # Original IR (constant)
        subprocess.run(["cp", "./data/target.bc", self.data_ir])
        subprocess.run(["cp", "./data/target.bc", self.tmp_ir])


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

    
    # Get execution speed (time) of ir
    #   Return average speed and stdev for SPEED_PROFILE_NUM experiments
    def get_speed (self, ir, flags):
        self.SPEED_PROFILE_NUM = 3
        performance_list = []
        for _ in range(self.SPEED_PROFILE_NUM):
            process = subprocess.Popen(["bash", "profile_speed.sh", ir, flags], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            performance = float(process.communicate()[0].strip())
            errmsg = str(process.communicate()[1])
            if errmsg != "":
                print("    ! (PROFILE_SPEED.SH ERR)  ERRMSG: ", errmsg)
            performance_list.append(performance)
        return (statistics.fmean(performance_list), statistics.stdev(performance_list))

    # Wrapper for get execution time
    #   Return average speed and stdev for SPEED_PROFILE_NUM experiments
    def get_speed_reward (self, action):
        # base_performance, base_stdev = self.get_speed(self.data_ir, "-no-flag")
        base_performance, base_stdev = self.get_speed(self.data_ir, BASE_FLAG)
        flags = ""
        for flag_idx in action:
            flags += (self.FLAG_LIST[flag_idx] + " ")
        performance, stdev = self.get_speed(self.tmp_ir, flags.strip())
        percent = round(((performance - base_performance) / base_performance)*100, 4)
        print("Speed improve: ", percent, "% (neg is good)")
        return percent


    def get_performance (self, ir, flags):
        process = subprocess.Popen(["bash", "compile_and_profile.sh", ir, flags], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        performance = int(process.communicate()[0].strip())
        errmsg = str(process.communicate()[1].strip())
        if errmsg != "":
            print("    ! (COMPILE_AND_PROFILE.SH ERR)  ERRMSG: ", errmsg)
        return performance


    def get_reward (self, action):
        # base_performance = self.get_performance(self.data_ir, "-no-flag")
        base_performance = self.get_performance(self.data_ir, BASE_FLAG)
        flags = ""
        for flag_idx in action:
            flags += (self.FLAG_LIST[flag_idx] + " ")
        performance = self.get_performance(self.tmp_ir, flags.strip())
        diff = (performance - base_performance)
        reward = - diff * 100  # low performance value is low memory usage
        percent = round((diff / base_performance)*100, 4)
        print("Memory difference: ", reward, ", Memory usage: ", percent, "% (neg is good)")
        return (reward, percent)


    def clear_tmp (self):
        tmp_dir_lists = os.listdir("./tmp")
        for tmp_dir in tmp_dir_lists:  # Empty tmp folders are done folder
            path = "./tmp/" + tmp_dir + "/"
            try:
                file_modified = datetime.fromtimestamp(os.path.getmtime(path))
            except:
                file_modified = datetime.datetime.now()
            if datetime.datetime.now() - file_modified > datetime.timedelta(seconds=60):
                print("Delete ", path)
                try:
                    os.rmdir(path)
                except:
                    pass


    def main (self):
        global IR_DIRECTORY_PATH

        # --------------------------
        # 
        # Test data config
        #   Test data are data that are not used for traiing
        #   TRAINING_USAGE value should be matched to that of RL_Train_Cluster.py
        #   IR file are loaded is ../Preprocess/clustered_ir/cluster_CLUSTER_IDX
        #   Test data should be matched with that of RL_Test_Cluster.py
        # 
        # --------------------------

        ir_file_lists = []
        TRAINING_USAGE = 0.7
        self.get_preprocess_values()
        for cluster_idx in range(CLUSTER_NUM):
            IR_DIRECTORY_PATH = IR_DIRECTORY_BASE_PATH + str(cluster_idx) + "/"
            tmp = os.listdir(os.fsencode(IR_DIRECTORY_PATH))
            tmp = list(map(os.fsdecode, tmp))
            tmp = [(IR_DIRECTORY_PATH + x) for x in tmp]
            ir_file_lists += tmp[int(len(tmp)*TRAINING_USAGE):]
        print("\n# Test dataset ", len(ir_file_lists))

        # --------------------------
        # 
        # RLLib Config
        # 
        # --------------------------

        # check running dir
        process = subprocess.Popen(["pwd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Current Directory (Please run at RL/): ", process.communicate()[0])

        # start Ray -- add `local_mode=True` here for debugging
        ray.init(ignore_reinit_error=True)

        # register the custom environment
        select_env = "memory-v0"
        register_env(select_env, lambda config: Memory_v0())

        # initialize data (initial ir for agent training)
        initial_ir = ir_file_lists[0]
        print(initial_ir)
        self.initialize_ir(initial_ir)

        # restoring checkpoint file
        chkpt_file = CHK_PATH

        # --------------------------
        # 
        # PPO Config
        # 
        # --------------------------

        # configure the environment and create agent
        if RL_ALGORITHM == "PPO": 
            config = ppo.DEFAULT_CONFIG.copy()
        elif RL_ALGORITHM == "A3C": 
            config = a3c.DEFAULT_CONFIG.copy()
        elif RL_ALGORITHM == "PG": 
            config = pg.DEFAULT_CONFIG.copy()

        config["framework"] = "tf2"
        config["eager_tracing"] = False # For debugging
        config["log_level"] = "ERROR" # DEBUG,INFO, ERROR
        config["horizon"] = 1000
        config["num_workers"] = 1
        config["train_batch_size"] = 256
        config["batch_mode"] = "complete_episodes"
        config["lr"] = 1e-3

        if RL_ALGORITHM == "PPO": 
            config["sgd_minibatch_size"] = 256 # for PPO
            agent = ppo.PPOTrainer(config, env=select_env) # train a policy with RLlib using PPO
        elif RL_ALGORITHM == "A3C": 
            agent = a3c.A3CTrainer(config, env=select_env) # train a policy with RLlib using A3C
        elif RL_ALGORITHM == "PG": 
            config["horizon"] = 256 # for PG
            config["lr"] = 0.0004 # for PG
            agent = pg.PGTrainer(config, env=select_env) # train a policy with RLlib using PG

        agent.restore(chkpt_file)

        # --------------------------
        # 
        # Testing
        # 
        # --------------------------

        policy = agent.get_policy()
        model = policy.model
        print(model.base_model.summary())

        reward_list = []
        memory_percent_list = []
        speed_percent_list = []
        for ir in ir_file_lists:
            print("Testing with ", ir)
            self.initialize_ir(ir)

            self.feature = self.get_feature()
            action = agent.compute_single_action(self.feature)

            if DEBUG:
                self.print_feature()
                self.print_action(action)
            reward, percent = self.get_reward(action)
            speed_percent = self.get_speed_reward(action)

            reward_list.append(reward)
            memory_percent_list.append(percent)
            speed_percent_list.append(speed_percent)

            self.clear_tmp()

        print("\n\nResult Summary (Compare with ", BASE_FLAG, ")")    
        print("Avg reward: ", round(statistics.mean(reward_list), 4),
                "\nMemory Usage: ", round(statistics.mean(memory_percent_list), 4), "% (neg is good)")
        print("Speed: ", round(statistics.mean(speed_percent_list), 4), "% (neg is good)")

        with open("./res/RL_Result.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Reward", "Memory (%)", "Speed (%)"])
            for idx in range(len(reward_list)):
                writer.writerow([str(reward_list[idx]), str(memory_percent_list[idx]), str(speed_percent_list[idx])])

if __name__ == "__main__":
    rl = RL_Test()
    rl.main()