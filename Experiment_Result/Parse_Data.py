import csv
import statistics

os_FILE = "../RL/res/Base_Result_-os.csv"
o3_FILE = "../RL/res/Base_Result_-o3.csv"
RESULT_FILE_LIST = [
    "../RL/res/RL_Result_PPO_os.csv",
    "../RL/res/RL_Cluster_Result_PPO_os.csv",
    "../RL/res/RL_Result_A3C_os.csv",
    "../RL/res/RL_Cluster_Result_A3C_os.csv",
    "../RL/res/RL_Result_PG_os.csv",
    "../RL/res/RL_Cluster_Result_PG_os.csv",
    "../RL/res/RL_Result_PPO_PG_A3C_os.csv",
    "../RL/res/RL_Cluster_Result_PPO_PG_A3C_os.csv",
]

raw_total_memory_list = []
raw_total_time_list = []

os_total_memory_list = []
os_memory_reduction_list = []
os_total_time_list = []
os_time_reduction_list = []

memory_result = []
time_result = []
with open(os_FILE, newline='') as f:
    reader = csv.reader(f)
    base_data = list(reader)
    del base_data[0]
    base_data = [list(map(float, lst)) for lst in base_data]

    for item in base_data:
        os_total_memory_list.append(int(item[0]))
        os_memory_reduction_list.append(int(item[1]))
        os_total_time_list.append(item[2])
        os_time_reduction_list.append(item[3])
        raw_total_memory_list.append(int(item[4]))
        raw_total_time_list.append(item[5])

    base_memory_reduction_percent_list = []
    for idx in range(len(os_memory_reduction_list)):
        diff = (os_memory_reduction_list[idx] / raw_total_memory_list[idx]) * 100
        base_memory_reduction_percent_list.append(diff)
    base_time_reduction_percent_list = []
    for idx in range(len(os_time_reduction_list)):
        diff = (os_time_reduction_list[idx] / raw_total_time_list[idx]) * 100
        base_time_reduction_percent_list.append(diff)

memory_result.append(base_memory_reduction_percent_list)
time_result.append(base_time_reduction_percent_list)


o3_total_memory_list = []
o3_memory_reduction_list = []
o3_total_time_list = []
o3_time_reduction_list = []

with open(o3_FILE, newline='') as f:
    reader = csv.reader(f)
    base_data = list(reader)
    del base_data[0]
    base_data = [list(map(float, lst)) for lst in base_data]

    for item in base_data:
        o3_total_memory_list.append(int(item[0]))
        o3_memory_reduction_list.append(int(item[1]))
        o3_total_time_list.append(item[2])
        o3_time_reduction_list.append(item[3])

for result_file in RESULT_FILE_LIST:
    print("Processing ", result_file)
    with open(result_file, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        del data[0]
        data = [list(map(float, lst)) for lst in data]

    memory_reduction_list = []
    for idx in range(len(data)):
        memory_value = int(-data[idx][0]/100)+os_total_memory_list[idx]
        diff = -(memory_value-raw_total_memory_list[idx])
        memory_reduction_list.append(diff)
    memory_reduction_precent_list = []
    for idx in range(len(memory_reduction_list)):
        diff = (memory_reduction_list[idx] / raw_total_memory_list[idx]) * 100
        memory_reduction_precent_list.append(diff)
    memory_result.append(memory_reduction_precent_list)

    time_reduction_list = []
    for idx in range(len(data)):
        time_value = data[idx][2]*os_total_time_list[idx]/100+os_total_time_list[idx]
        diff = -(time_value-raw_total_time_list[idx])
        time_reduction_list.append(diff)
    time_reduction_percent_list = []
    for idx in range(len(time_reduction_list)):
        diff = (time_reduction_list[idx] / raw_total_time_list[idx]) * 100
        time_reduction_percent_list.append(diff)
    time_result.append(time_reduction_percent_list)
    
print("\nMemory Average")
memory_average_percent = list(map(statistics.mean, memory_result))
for idx in range(1, len(memory_average_percent)):
    print(RESULT_FILE_LIST[idx-1].split('/')[3], "Improve compare to -os: ", 
    round((memory_average_percent[idx]-memory_average_percent[0])/memory_average_percent[0]*100, 3), "%")

print("\nTime Average")
time_average_percent = list(map(statistics.mean, time_result))
for idx in range(1, len(time_average_percent)):
    print(RESULT_FILE_LIST[idx-1].split('/')[3], "Improve compare to -os: ", 
    round((time_average_percent[idx]-time_average_percent[0])/time_average_percent[0]*100, 3), "%")

memory_result = list(map(list, zip(*memory_result)))
with open("./Memory_Result.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow([os_FILE] + RESULT_FILE_LIST)
    for idx in range(1, len(memory_result)):
        writer.writerow(memory_result[idx])