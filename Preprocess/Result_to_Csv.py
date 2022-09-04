import sys
import pandas as pd

if len(sys.argv) != 2:
    print("Wrong usage")
    exit()

flags = []
irs = []
res_file = sys.argv[1]

with open("./data/Flag_Candidates.in", "r") as f:
    while True:
        line = f.readline().strip()
        if len(line)==0: break
        flags.append(line)

with open("./data/IR_Candidates.in", "r") as f:
    while True:
        line = f.readline().strip()
        if len(line)==0: break
        irs.append(line.split('.')[0])

res_matrix = []
for i in range(len(irs)):
    res_matrix.append(list())
    for j in range(len(flags)):
        res_matrix[i].append(0)

with open(res_file, "r") as f:
    while True:
        line = f.readline().strip()
        if len(line)==0: break
        line_list = line.split()
        cur_flag = line_list[0]
        cur_ir = line_list[1]
        cur_res = line_list[2]

        res_matrix[irs.index(cur_ir)][flags.index(cur_flag)] = cur_res

df = pd.DataFrame(res_matrix, columns=flags, index=irs)
df.to_csv("./data/Flag_Profile.csv", sep=",")