import pandas as pd
from os import listdir
import subprocess
import pickle as pk
from os.path import isfile, join
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

valid_ir_file_names = []
feature_matrix = []
features = []

with open("./data/Feature_Candidates.in", "r") as f:
    while True:
        s = f.readline().strip()
        if len(s)==0: break
        features.append(s)

with open("./Valid_IR.txt", "r") as f:
    while True:
        s = f.readline().strip().split('.')[0]
        if len(s)==0: break
        valid_ir_file_names.append(s)

feature_file_names = [("../Feature_Extraction/feature/" + f) for f in listdir("../Feature_Extraction/feature/") 
    if isfile(join("../Feature_Extraction/feature/", f))]
feature_file_names.sort()

# Only use feature of valide ir files
tmp = []
for feature_file_name in feature_file_names:
    file_name = feature_file_name.split('/')[3].split('.')[0]
    if file_name in valid_ir_file_names: tmp.append(feature_file_name)
feature_file_names = tmp

file_idx = 0
for feature_file_name in feature_file_names:
    # Read from randome generated file features
    cur_file_feature = []
    with open(feature_file_name, "r") as f:
        feature_idx = 0
        while True:
            strs = f.readline().strip().split()
            if len(strs)==0: break
            if strs[0] != features[feature_idx]:
                print("Error! This feature is not supposed to be here!")
                quit()
            cur_file_feature.append(strs[1])
            feature_idx += 1

    # Save to pandas dataframe for ananlysis
    feature_matrix.append(cur_file_feature)

df = pd.DataFrame(feature_matrix, columns=features)
df.to_csv("./data/Feature_Matrix.csv", sep=",")
x = df.loc[:, features].values
sc = StandardScaler()
x = sc.fit_transform(x)

# PCA
pca = PCA(0.99)
principal_components = pca.fit_transform(x)
principal_df = pd.DataFrame(data=principal_components)
print("Number of compnents: ", len(pca.explained_variance_ratio_))
print("Total explained varaince ratio: ", round(sum(pca.explained_variance_ratio_)*100, 5))
print("Maximum coeff: ", max(map(max, map(abs, principal_components)))) # used for RL input function

# Save PCA info
with open("Feature_PCA_Result.txt", "w") as f:
    f.write(str(len(pca.explained_variance_ratio_)) + "\n")
    f.write(str(int(max(map(max,principal_components)) + 10)))

# Save PCA and StandarScalar model
pk.dump(pca, open("./data/pca_train.pkl", "wb"))
pk.dump(sc, open("./data/std_scalar.pkl", "wb"))

# Save PCA results for each ir files
subprocess.run(["rm", "-f", "./pca_result/No_Cluster/*.in"])
for file_idx in range(len(feature_file_names)):
    feature_file_name = feature_file_names[file_idx]
    pca_result = principal_components[file_idx]
    pca_result_file_name = "./pca_result/No_Cluster/" + feature_file_name.split('/')[3]
    with open(pca_result_file_name, "w") as f:
        f.write(str(len(principal_components[0])) + "\n")
        for res in pca_result:
            f.write(str(res) + "\n")