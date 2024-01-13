# Main python script

#from functions import functions.k-d.py, functions.quad.py, functions.range.py, functions.r.py, functions.lsh.py
from functions import lsh
import os, json

path = os.path.abspath(os.getcwd())
with open(path + "\\data\\out2.json", "r", encoding="utf-8") as f:
    jdata = json.load(f)



data = []
go_back = []
for c, i in enumerate(jdata):
    if 'education' in i.keys():
        data.append(i['education'])
        go_back.append(c)





lsh.shing_minhash_lsh(data, k=3, C=100, B=50, threshold=0.35)




