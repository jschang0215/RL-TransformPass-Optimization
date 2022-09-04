import pandas as pd
import sys
from os import listdir
import pickle as pk
from os.path import isfile, join
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# PCA to extracted feature
#   Get PCA result of the given (argv[1]) feature file
#   Store in ./data/feature.in
#       Output: 
#               1st line number of pca components
#               2nd ~ value of pca

pca = pk.load(open("../Preprocess/data/pca_train.pkl", "rb"))
sc = pk.load(open("../Preprocess/data/std_scalar.pkl", "rb"))
feature_file = sys.argv[1]
output_file = sys.argv[2]
features = []
cur_feature = []

# Get possible features
with open("../Preprocess/data/Feature_Candidates.in", "r") as f:
    while True:
        s = f.readline().strip()
        if len(s)==0: break
        features.append(s)

# Read feature file
with open(feature_file, "r") as f:
    feature_idx = 0
    while True:
        strs = f.readline().strip().split()
        if len(strs)==0: break
        if strs[0] != features[feature_idx]:
            print("Error! This feature is not supposed to be here!")
            quit()
        cur_feature.append(strs[1])
        feature_idx += 1

# Normalize factor to [-1.0 1.0]
#   Normalize factor is estimated maximum pca value
with open("../Preprocess/Feature_PCA_Result.txt", "r") as f:
    _ = f.readline() # num of principal components
    normalize_factor = int(f.readline().strip())

cur_feature = [cur_feature]
df = pd.DataFrame(cur_feature, columns=features)
x = df.loc[:, features].values
x = sc.transform(x)

# Get PCA result of single vector
principal_components = pca.transform(x)
principal_components = principal_components / normalize_factor # normailize to [-1.0 1.0]
principal_df = pd.DataFrame(data=principal_components)

# Output PCA feature to ./data
with open(output_file, "w") as f:
    f.write(str(len(principal_components[0])) + "\n")
    for val in principal_components[0]:
        f.write(str(val) + "\n")

