import sys

c_file = sys.argv[1]
res_code = ""

with open(c_file, "r") as f:
    while True:
        line = f.readline()
        if len(line)==0: break
        if "printf" not in line:
            res_code += line

with open(c_file, "w") as f:
    f.write(res_code)
        