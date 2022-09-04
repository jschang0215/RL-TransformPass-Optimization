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

DEBUG = True
BASE_FLAG = "-o3"

CLUSTER_NUM = 4
INITIAL_CLUSTER_IDX = 0
IR_DIRECTORY_BASE_PATH="../Preprocess/clustered_ir/cluster_"
IR_DIRECTORY_PATH="../Preprocess/clustered_ir/cluster_" + str(INITIAL_CLUSTER_IDX) + "/"

class RL_Test_Base ():

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
    def get_time (self):
        base_performance, base_stdev = self.get_speed(self.data_ir, "-no-flag")
        performance, stdev = self.get_speed(self.data_ir, BASE_FLAG)
        diff = - (performance - base_performance)
        return (performance, diff, base_performance)


    def get_performance (self, ir, flags):
        process = subprocess.Popen(["bash", "compile_and_profile.sh", ir, flags], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        performance = int(process.communicate()[0].strip())
        errmsg = str(process.communicate()[1].strip())
        if errmsg != "":
            print("    ! (COMPILE_AND_PROFILE.SH ERR)  ERRMSG: ", errmsg)
        return performance


    def get_memory (self):
        base_performance = self.get_performance(self.data_ir, "-no-flag")
        performance = self.get_performance(self.tmp_ir, BASE_FLAG)
        diff = - (performance - base_performance)
        return (performance, diff, base_performance)


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
        # Testing
        # 
        # --------------------------

        total_memory_list = []
        memory_reduction_list = []
        total_time_list = []
        time_reduction_list = []
        base_total_memory_list = []
        base_total_time_list = []
        for ir in ir_file_lists:
            print("Testing with ", ir)
            self.initialize_ir(ir)

            total_memory, memory_reduction, base_memory = self.get_memory()
            total_time, time_reduction, base_time = self.get_time()

            total_memory_list.append(total_memory)
            memory_reduction_list.append(memory_reduction)
            total_time_list.append(total_time)
            time_reduction_list.append(time_reduction)
            base_total_memory_list.append(base_memory)
            base_total_time_list.append(base_time)

            self.clear_tmp()

        with open("./res/Base_Result_" + BASE_FLAG + ".csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Total Memory", "Memory Reduction (b)", "Total Time", "Time Reduction (s)", "Base Total Memory", "Base Total Time (s)"])
            for idx in range(len(total_memory_list)):
                writer.writerow([   str(total_memory_list[idx]), str(memory_reduction_list[idx]), 
                                    str(total_time_list[idx]), str(time_reduction_list[idx]),
                                    str(base_total_memory_list[idx]), str(base_total_time_list[idx]),
                                ])

if __name__ == "__main__":
    rl = RL_Test_Base()
    rl.main()