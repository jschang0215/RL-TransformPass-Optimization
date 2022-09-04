#!/usr/bin/env python
from distutils.command.config import config
from tracemalloc import start
from rl_env.envs.memory_env import Memory_v0
from ray.tune.registry import register_env
import gym
import subprocess
import os
import ray
import ray.tune as tune
import ray.rllib.agents.ppo as ppo
import ray.rllib.agents.a3c as a3c
import ray.rllib.agents.pg as pg
import ray.rllib.agents.sac as sac
import shutil
import time
import random
import datetime

RL_ALGORITHM = "PG"
TRAINING_USAGE = 0.7
CLUSTER_NUM = 4
IR_DIRECTORY_BASE_PATH="../Preprocess/clustered_ir/cluster_"
IR_DIRECTORY_PATH="../Preprocess/clustered_ir/cluster_0/"

def initialize_ir(ir):
    original_path = ir
    new_path = "./data/target.bc"
    subprocess.run(["cp", original_path, new_path])

def main ():
    global IR_DIRECTORY_PATH
    global TRAINING_USAGE

    # --------------------------
    # 
    # Train data config
    #   TRAINING_USAGE value should be matched to that of RL_Train_Cluster.py
    #   IR file are loaded is ../Preprocess/clustered_ir/cluster_CLUSTER_IDX
    #   Train data should be matched with that of RL_Test.py
    # 
    # --------------------------

    ir_file_lists = []
    for cluster_idx in range(CLUSTER_NUM):
        IR_DIRECTORY_PATH = IR_DIRECTORY_BASE_PATH + str(cluster_idx) + "/"
        tmp = os.listdir(os.fsencode(IR_DIRECTORY_PATH))
        tmp = list(map(os.fsdecode, tmp))
        tmp = [(IR_DIRECTORY_PATH + x) for x in tmp]
        ir_file_lists += tmp[0:int(len(tmp)*TRAINING_USAGE)]
    random.shuffle(ir_file_lists)
    print("\n# Train dataset ", len(ir_file_lists))

    # --------------------------
    # 
    # RLLib Config
    # 
    # --------------------------

    # check running dir
    process = subprocess.Popen(["pwd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Current Directory (Please run at RL/): ", process.communicate()[0])

    # init directory in which to save checkpoints
    chkpt_root = "./rllib/exa"
    shutil.rmtree(chkpt_root, ignore_errors=True, onerror=None)

    # init directory in which to log results
    ray_results = "./rllib/ray_results/"
    shutil.rmtree(ray_results, ignore_errors=True, onerror=None)

    # start Ray -- add `local_mode=True` here for debugging
    ray.init(ignore_reinit_error=True)

    # register the custom environment
    select_env = "memory-v0"
    register_env(select_env, lambda config: Memory_v0())

    # initialize data (initial ir for agent training)
    initial_ir = ir_file_lists[0]
    initialize_ir(initial_ir)

    # --------------------------
    # 
    # RL Algorithm Config
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
    config["num_workers"] = 14
    config["train_batch_size"] = 256
    config["batch_mode"] = "complete_episodes"
    config["lr"] = 1e-3

    if RL_ALGORITHM == "PPO": 
        config["sgd_minibatch_size"] = 256 # for PPO
        agent = ppo.PPOTrainer(config, env=select_env) # train a policy with RLlib using PPO
        n_iter = 2
    elif RL_ALGORITHM == "A3C": 
        agent = a3c.A3CTrainer(config, env=select_env) # train a policy with RLlib using A3C
        n_iter = 2
    elif RL_ALGORITHM == "PG": 
        config["horizon"] = 256 # for PG
        config["num_workers"] = 15
        config["lr"] = 0.0004 # for PG
        agent = pg.PGTrainer(config, env=select_env) # train a policy with RLlib using PG
        n_iter = 1 # for PG

    status = "{}: {:2d} | Reward {:6.2f} / {:6.2f} | Saved {}"

    # --------------------------
    # 
    # Training
    # 
    # --------------------------

    start_time = time.time()
    idx = 0
    for ir in ir_file_lists:
        ir = os.fsdecode(ir)
        print("Training with ", ir)
        initialize_ir(ir)

        for itr in range(1, n_iter+1):
            result = agent.train()
            chkpt_file = agent.save(chkpt_root)

            print(status.format(
                    ir, itr,
                    result["episode_reward_mean"],
                    result["episode_reward_max"],
                    chkpt_file
                    ))

        idx += 1
        print("Elapsed Tiem: ", str(datetime.timedelta(seconds=time.time()-start_time)),
                "Estimated Time Left: ", str(datetime.timedelta(seconds=(time.time()-start_time)/idx*(len(ir_file_lists)-idx))))


    # examine the trained policy
    policy = agent.get_policy()
    model = policy.model
    print(model.base_model.summary())


if __name__ == "__main__":
    main()