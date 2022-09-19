# ML Compiler Flag Optimization for Reducing Memory Consumption

This is the source code repository of our work "Optimizing LLVM Transform Passes Sequence with Reinforcement Learning for Reducing Runtime Memory Profile", under review at DATE 2023. This study aims to optimize memory usage by optimizing LLVM optimization flags using reinforcement learning. The repository in consisted of the followings:

## 1. Feature Extraction

`Feature_Extraction/` includes randomly generated source codes and feature extraction LLVM pass. More information is in `Feature_Extraction/README.md`.

## 2. Preprocessing

`Preprocess/` includes flag and IR selection that are used for the RL model. It also reduces feature dimension by applying PCA and KMeans clustering to the raw features. More information is in `Preprocess/README.md`.

## 3. Reinforcement Learning

`RL/` includes RL training and testing models. PPO, A3C, PG algorithms are investigated. More information and experiment result is in `RL/README.md`.


