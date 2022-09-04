import sys
sys.path.append('./msparser')
import msparser

if len(sys.argv) < 2:
    print("Pass massif.out file")
    exit()

data = msparser.parse_file(sys.argv[1])
total_mem = []
# print("# valgrind --tool=massif", data['desc'], data['cmd'])
for snapshot in data['snapshots']:
    stack = snapshot['mem_stack']
    heap = snapshot['mem_heap']
    extra = snapshot['mem_heap_extra']
    # print(heap, extra, heap + extra)
    total_mem.append(heap + extra + stack)
print(max(total_mem))