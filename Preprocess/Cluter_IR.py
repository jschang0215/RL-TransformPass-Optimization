from cmath import isnan, nan
from os import listdir
import pandas as pd
from os.path import isfile, join
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import subprocess
import pickle as pk
import math

pca_results = []
pca_num = 15

pca_file_names = [("./pca_result/No_Cluster/" + f) for f in listdir("./pca_result/No_Cluster/") 
    if isfile(join("./pca_result/No_Cluster/", f))]
pca_file_names.sort()

for pca_file_name in pca_file_names:
    cur_pca_result = []
    with open(pca_file_name, "r") as f:
        pca_num = int(f.readline().strip())
        for _ in range(pca_num):
            pca_val = float(f.readline().strip())
            cur_pca_result.append(pca_val)
    pca_results.append(cur_pca_result)

df = pd.DataFrame(pca_results)
print(df)

# Elbow Method for determining cluster num
dist_sum = []
K = range(1, 20)
for k in K:
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(df)
    kmeans_result = df.copy()
    kmeans_result["cluster"] = kmeans.labels_
    dist_sum.append(kmeans.inertia_)
plt.plot(K, dist_sum, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method For Optimal k') # Optimal value is 4
plt.show()

# Save file grouped to each cluster in ./cluster_pac_result
CLUSTER_NUM = 4

kmeans = KMeans(n_clusters=CLUSTER_NUM)
kmeans.fit(df)
pk.dump(kmeans, open("./data/kmeans_train.pkl", "wb")) # save model
kmeans_result = df.copy()
kmeans_result["cluster"] = kmeans.labels_
clustered_result = [[] for _ in range(CLUSTER_NUM)]
clustered_ir = [[] for _ in range(CLUSTER_NUM)]
for idx, row in kmeans_result.iterrows():
    clustered_result[int(row["cluster"])].append(row[0:pca_num].to_list())
    clustered_ir[int(row["cluster"])].append(pca_file_names[idx].split('/')[3].split('.')[0] + ".bc")

# Save clustered PCA result
subprocess.run(["rm", "-r", "./pca_result/Clustered"])
subprocess.run(["mkdir", "./pca_result/Clustered"])
for cluster_idx in range(CLUSTER_NUM):
    subprocess.run(["mkdir", "./pca_result/Clustered/cluster_" + str(cluster_idx)])
    print("# Cluster (", cluster_idx, ") element: ", len(clustered_result[cluster_idx]))

    file_idx = 0
    for cluster_ele in clustered_result[cluster_idx]:
        file_name = "./pca_result/Clustered/cluster_" + str(cluster_idx) + "/" + str(file_idx) + ".in"
        with open(file_name, "w") as f:
            f.write(str(pca_num) + "\n")
            for val in cluster_ele:
                f.write(str(val) + "\n")
        file_idx += 1

# Save ir according to clustered
subprocess.run(["rm", "-r", "./clustered_ir"])
subprocess.run(["mkdir", "./clustered_ir"])
for cluster_idx in range(CLUSTER_NUM):
    subprocess.run(["mkdir", "./clustered_ir/cluster_" + str(cluster_idx)])
    for ir_file_name in clustered_ir[cluster_idx]:
        original_ir = "../Feature_Extraction/ir/" + ir_file_name
        new_ir = "./clustered_ir/cluster_" + str(cluster_idx) + "/" + ir_file_name
        subprocess.run(["cp", original_ir, new_ir])