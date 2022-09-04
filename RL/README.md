# Reinforcement Learning

This folder contains reinforcement learning codes. 

## 1. Gym Environment

**Environment for RL.** `rl_env/` folder contains environment configuration where observation space, state, actions, reward functions are defined.

* `rl_env/memory_env.py`: Environment used in this work

## 2. RL model

**RL model used for training and testing.** RL model implemented with [ray rllib](https://docs.ray.io/en/latest/rllib/rllib-algorithms.html). We trained and tested our model with PPO, A3C, PG. We used 14 cores in Ryzen 5900X on Ubuntu 22.04 for training which takes 3 to 17 hours depending on used algorithm. 

* `RL_Train.py`: Train RL model
  * `clear_RL.sh`: Clear files for new training
  * `compile_and_profile.sh`: Profile memory usage
  * `profile_speed.sh`: Profile speed
  * `Feature_PCA.py`: Get PCA feature with raw feature data
  * `feature_extract.sh`: PCA feature is extracted from source code by generating IR code, applying flag, extract feature with `../Feature_Extraction/build/Feature.so`, and apply PCA with `Feature_PCA.py`
  * `rllib/exa`: Checkpoints are stored here when training
* `RL_Test.py`: Test RL model
* `checkpoints/`: Saved model of the trained model
* `tensorboard_logs/`: Saved tensorboard logs of the trained model

## 3. Etc

* `old`: Files used as prototype
* `data/`, `tmp/`: Temporary folder used by scripts

## 4. Results

Reward is compared with base performance when profiled with `-o3` option. 12 flags are used as action. 32 flags are used as candidates

### Without Clustering

#### PPO

* Compared with `-o0`

  ```
  Result Summary (Compare with  -o0 )
  Avg reward:  9838.806 
  Memory Usage:  -0.3876 % (neg is good)
  Speed:  -0.5278 % (neg is good)
  ```

* Compared with `-o3`

  ```
  Result Summary (Compare with  -o3 )
  Avg reward:  9982.0896 
  Memory Usage:  -0.3861 % (neg is good)
  Speed:  -0.6351 % (neg is good)
  ```

* Compared with `-os`

  ```
  Result Summary (Compare with  -Os )
  Avg reward:  0 
  Memory Usage:  -0.0163 % (neg is good)
  Speed:  0.3448 % (neg is good)
  ```

#### A3C

* Compared with `-o0`

  ```
  Result Summary (Compare with  -o0 )
  Avg reward:  9719.403 
  Memory Usage:  -0.3838 % (neg is good)
  Speed:  -0.617 % (neg is good)
  ```

* Compared with `-o3`

  ```
  Result Summary (Compare with  -o3 )
  Avg reward:  9719.403 
  Memory Usage:  -0.385 % (neg is good)
  Speed:  -0.8366 % (neg is good)
  ```

* Compared with `-os`

  ```
  Result Summary (Compare with  -Os )
  Avg reward:  358.209 
  Memory Usage:  -0.0104 % (neg is good)
  Speed:  0.2259 % (neg is good)
  ```

#### PG

* Compared with `-o0`

  ```
  Result Summary (Compare with  -o0 )
  Avg reward:  9886.5672 
  Memory Usage:  -0.3899 % (neg is good)
  Speed:  -1.1965 % (neg is good)
  ```
  
* Compared with `-o3`

  ```
  Result Summary (Compare with  -o3 )
  Avg reward:  9552.2388 
  Memory Usage:  -0.3732 % (neg is good)
  Speed:  -0.9973 % (neg is good)
  ```

* Compared with `-os`

  ```
  Result Summary (Compare with  -Os )
  Avg reward:  262.6866 
  Memory Usage:  -0.0074 % (neg is good)
  Speed:  0.2228 % (neg is good)
  ```

#### PPO+A3C+PG

* Compared with `-o0`

  ```
  Result Summary (Compare with  -o0 )
  Avg reward:  10244.7761 
  Memory Usage:  -0.4031 % (neg is good)
  Speed:  -2.3999 % (neg is good)
  ```

* Compared with `-o3`

  ```
  Result Summary (Compare with  -o3 )
  Avg reward:  10197.0149 
  Memory Usage:  -0.402 % (neg is good)
  Speed:  -2.3741 % (neg is good)
  ```

* Compared with `-os`

  ```
  Result Summary (Compare with  -Os )
  Avg reward:  859.7015 
  Memory Usage:  -0.0384 % (neg is good)
  Speed:  -1.5494 % (neg is good)
  ```

### Clustering

#### PPO

* Compared with `-o0`

  ```
  Result Summary (Compare with  -o0 )
  Avg reward:  11414.9254 
  Memory Usage:  -0.456 % (neg is good)
  Speed:  -1.8618 % (neg is good)
  ```

* Compared with `-o3`

  ```
  Result Summary (Compare with  -o3 )
  Avg reward:  11295.5224 
  Memory Usage:  -0.4585 % (neg is good)
  Speed:  -1.758 % (neg is good)
  ```

* Compared with `-os`

  ```
  Result Summary (Compare with  -Os )
  Avg reward:  3271.6418 
  Memory Usage:  -0.1317 % (neg is good)
  Speed:  -0.6187 % (neg is good)
  ```

#### A3C

* Compared with `-o0`

  ```
  Result Summary (Compare with  -o0 )
  Avg reward:  10316.4179 
  Memory Usage:  -0.4166 % (neg is good)
  Speed:  -2.857 % (neg is good)
  ```

* Compared with `-o3`

  ```
  Result Summary (Compare with  -o3 )
  Avg reward:  10268.6567 
  Memory Usage:  -0.4149 % (neg is good)
  Speed:  -2.6517 % (neg is good)
  ```

* Compared with `-os`

  ```
  Result Summary (Compare with  -Os )
  Avg reward:  1217.9104 
  Memory Usage:  -0.0558 % (neg is good)
  Speed:  -1.3171 % (neg is good)
  ```

#### PG

* Compared with `-o0`

  ```
  Result Summary (Compare with  -o0 )
  Avg reward:  10722.3881 
  Memory Usage:  -0.4298 % (neg is good)
  Speed:  -1.8669 % (neg is good)
  ```

* Compared with `-o3`

  ```
  Result Summary (Compare with  -o3 )
  Avg reward:  10459.7015 
  Memory Usage:  -0.4267 % (neg is good)
  Speed:  -1.7095 % (neg is good)
  ```

* Compared with `-os`

  ```
  Result Summary (Compare with  -Os )
  Avg reward:  1695.5224 
  Memory Usage:  -0.0731 % (neg is good)
  Speed:  -1.1744 % (neg is good)
  ```

#### PPO+A3C+PG

* Compared with `-o0`

  ```
  Result Summary (Compare with  -o0 )
  Avg reward:  12465.6716 
  Memory Usage:  -0.497 % (neg is good)
  Speed:  -3.3807 % (neg is good)
  ```

* Compared with `-o3`

  ```
  Result Summary (Compare with  -o3 )
  Avg reward:  12346.2687 
  Memory Usage:  -0.4929 % (neg is good)
  Speed:  -3.2124 % (neg is good)
  ```

* Compared with `-os`

  ```
  Result Summary (Compare with  -Os )
  Avg reward:  3128.3582 
  Memory Usage:  -0.1322 % (neg is good)
  Speed:  -2.6498 % (neg is good)
  ```

## 5. Appendix

### Flag candidates

These are the 32 flag candidates used for RL action candidates.

|     Flags     |     Flags      |     Flags     |          Flags          |
| :-----------: | :------------: | :-----------: | :---------------------: |
|     -adce     | -always-inline | -argpromotion |       -constmerge       |
|     -dce      |  -deadargelim  |     -dse      |       -globaldce        |
|  -globalopt   |      -gvn      | -instcombine  | -aggressive-instcombine |
|    -ipsccp    |     -lcssa     |     -licm     |     -loop-deletion      |
| -loop-extract |  -loop-reduce  | -loop-rotate  |     -loop-simplify      |
| -loop-unroll  |  -loweratomic  | -lowerinvoke  |      -lowerswitch       |
|  -memcpyopt   |   -mergefunc   | -mergereturn  |      -reassociate       |
|     -sroa     |     -sccp      |     -sink     |         -strip          |

