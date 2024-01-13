from functions import str_int, r, lsh
import os, json

path = os.path.abspath(os.getcwd())
with open(path + "\\data\\out2.json", "r", encoding="utf-8") as f:
    jdata = json.load(f)

rr = r.rtree(jdata)
rr.build_tree()
#rr.print_tree()
ids = rr.search("a","z",0,0,13)
#print(ids)

educations = []
for id in ids:
    educations.append(jdata[id]["education"])

groups = lsh.shing_minhash_lsh(educations, k=3, C=100, B=50, threshold=0.4, plot_threshold=0)
#print(groups)

similar_ids = []
for g in groups:
    id_g = []
    for i in g:
        id_g.append(ids[i])
    similar_ids.append(id_g)

#print(similar_ids)

for sids in similar_ids:
    if len(sids)>20:
        continue
    for sid in sids:
        print(jdata[sid]["education"]+"---------------")
    print("")

