import pandas as pd
from statsmodels.stats.weightstats import ztest as ztest

df = pd.read_csv("./data/Flag_Profile.csv")
mu = 0
try:
    mu = df['-no-flag'].mean()
except:
    print("No -no-flag data")
    exit()

good_irs = set()

for flag in df.keys():
    if flag=='Unnamed: 0' or flag=='-no-flag': continue
    zvalue, pvalue = ztest(df[flag].tolist(), value=mu)

    diff_num = 0
    for ir_idx in range(len(df[flag].tolist())):
        if df[flag].tolist()[ir_idx] < df['-no-flag'].tolist()[ir_idx]:
            # print("    " + df['Unnamed: 0'].tolist()[ir_idx])
            good_irs.add(df['Unnamed: 0'].tolist()[ir_idx] + ".bc")
            diff_num += 1

    if zvalue<0 and pvalue < 1.0:
        print(flag, pvalue, diff_num)

print(good_irs)
print(len(good_irs))

with open("Valid_IR.txt", "w") as f:
    for ir in good_irs:
        f.write(ir + "\n")