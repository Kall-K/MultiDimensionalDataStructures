import os, string


counter = 0 
lines = ""

path = os.path.abspath(os.getcwd())
with open(path + "\\data\\out.json", "r", encoding="utf-8") as f:  # 785
    for i in f.readlines():
        for j in i:
            if j not in string.printable:
                counter += 1
                continue                
            lines += j

with open(path + "\\data\\out2.json", "w", encoding="utf-8") as f:
    f.writelines(lines)


print(counter)