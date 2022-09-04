#!/usr/bin/env python
from tracemalloc import start
from rl_env.envs.memory_env import Memory_v0
from ray.tune.registry import register_env
import gym
import subprocess
import os
import ray
import ray.tune as tune
import ray.rllib.agents.ppo as ppo
import shutil
import time

IR_DIRECTORY_PATH="../Feature_Extraction/ir/"

def initialize_ir(ir):
    original_path = IR_DIRECTORY_PATH + ir
    new_path = "./data/target.bc"
    subprocess.run(["cp", original_path, new_path])
    tmp_path = "./tmp/target.bc"
    subprocess.run(["cp", new_path, tmp_path])

def main ():
    # check running dir
    process = subprocess.Popen(["pwd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Current Directory (Please run at RL/): ", process.communicate()[0])

    # init directory in which to save checkpoints
    chkpt_root = "./rllib/exa"
    shutil.rmtree(chkpt_root, ignore_errors=True, onerror=None)

    # init directory in which to log results
    ray_results = "./rllib/ray_results/".format(os.getenv("HOME"))
    shutil.rmtree(ray_results, ignore_errors=True, onerror=None)


    # start Ray -- add `local_mode=True` here for debugging
    ray.init(ignore_reinit_error=True)

    # register the custom environment
    select_env = "memory-v0"
    register_env(select_env, lambda config: Memory_v0())

    # initialize data (initial ir for agent training)
    initial_ir = os.fsdecode(os.listdir(os.fsencode(IR_DIRECTORY_PATH))[0])
    initialize_ir(initial_ir)

    # configure the environment and create agent
    config = ppo.DEFAULT_CONFIG.copy()
    config["framework"] = "tf2"
    config["eager_tracing"] = False # For debugging
    config["log_level"] = "ERROR" # DEBUG,INFO, ERROR
    config["horizon"] = 1000
    config["num_workers"] = 1
    # config["num_gpus"] = 1
    # config["num_workers"] = 12
    config["lr"] = 1e-3
    agent = ppo.PPOTrainer(config, env=select_env)

    status = "{:2d} reward {:6.2f}/{:6.2f}/{:6.2f} len {:4.2f} saved {}"
    n_iter = 500

    # train a policy with RLlib using PPO
    # Loop through ir files
    ir_file_lists = os.listdir(os.fsencode(IR_DIRECTORY_PATH))
    start_time = time.time()
    idx = 0
    for ir in ir_file_lists:
        ir = os.fsdecode(ir)
        print("Training with ", ir)
        initialize_ir(ir)

        for n in range(n_iter):
            result = agent.train()
            chkpt_file = agent.save(chkpt_root)

            print(status.format(
                    n + 1,
                    result["episode_reward_min"],
                    result["episode_reward_mean"],
                    result["episode_reward_max"],
                    result["episode_len_mean"],
                    chkpt_file
                    ))

            idx += 1
            print("Estimated Time Left: ", 
                    (time.time() - start_time) * (n_iter * len(ir_file_lists) - idx) / 3600)


    # examine the trained policy
    policy = agent.get_policy()
    model = policy.model
    print(model.base_model.summary())


if __name__ == "__main__":
    main()