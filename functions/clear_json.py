import os, string, json


counter = 0
lines = ""

# remove bad characters
path = os.path.abspath(os.getcwd())
with open(path + "\\data\\out.json", "r", encoding="utf-8") as f:  # 785
    for i in f.readlines():
        for j in i:
            if j not in string.printable:
                counter += 1
                continue                
            lines += j


jdata = json.loads(lines)

final_data = []
for i in range(len(jdata)):
    final_data.append({})

for i in range(len(jdata)):
    final_data[i]["name"]=jdata[i]["name"]
    final_data[i]["awards"]=jdata[i]["awards"]
    
    if "education" not in jdata[i].keys():
        final_data[i]["education"]="No education found."
    else:
        final_data[i]["education"]=jdata[i]["education"]

    final_data[i]["dblp_records"]=jdata[i]["dblp_records"]


with open(path + "\\data\\out2.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=4)


print("Bad characters: " + str(counter))