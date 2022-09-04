# Optimizing LLVM Transform Passes with Reinforcement Learning for Reducing Memory Consumption

This is the source code repository of our work "Optimizing LLVM Transform Passes with Reinforcement Learning for Reducing Memory Consumption". This study aims to optimize memory usage by optimizing LLVM optimization flags using reinforcement learning. The repository in consisted of the followings:

## 1. Feature Extraction

![1](.\fig\1.jpg)

`Feature_Extraction/` includes randomly generated source codes and feature extraction LLVM pass. More information is in `Feature_Extraction/README.md`.

## 2. Preprocessing

![3](.\fig\3.jpg)

`Preprocess/` includes flag and IR selection that are used for the RL model. It also reduces feature dimension by applying PCA and KMeans clustering to the raw features. More information is in `Preprocess/README.md`.

## 3. Reinforcement Learning

![4](.\fig\4.jpg)

`RL/` includes RL training and testing models. PPO, A3C, PG algorithms are investigated. More information and experiment result is in `RL/README.md`.

------

Codes and ideas are all by [Juneseo Chang](https://jschang0215.github.io/) during his undergraduate research intern at [AI-SoC Lab](https://ai-soc.github.io/). Contact [jschang0215@snu.ac.kr](mailto:jschang0215@snu.ac.kr) for issues.
