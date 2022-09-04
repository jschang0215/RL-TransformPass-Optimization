from gym.envs.registration import register

register(
    id="memory-v0",
    entry_point="rl_env.envs:Memory_v0",
    max_episode_steps=1000,
)