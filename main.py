# Main python script

#from functions import functions.k-d.py, functions.quad.py, functions.range.py, functions.r.py, functions.lsh.py
from functions import quad#,lsh
import os, json
from timeit import default_timer as timer


path = os.path.abspath(os.getcwd())
with open(path + "\\data\\out2.json", "r", encoding="utf-8") as f:
    jdata = json.load(f)

#build quadTree
tic = timer()
octree, max_x = quad.init_quadTree(jdata)
toc = timer()
#end 
print(f"(QuaTree-Build)ellapsed time: {toc-tic} sec")
#range query quadTree
ranges = [[0,max_x],[0,1],[quad.str_to_int("a"),quad.str_to_int("b")]]
quad_nodes = []
tic = timer()
quad_nodes = octree.range_query(octree.root, ranges, quad_nodes)
tic = timer()
print(f"(QuaTree-RangeQuery)ellapsed time: {tic-toc} sec")
#end

for qn in quad_nodes:
    print(f"coordinates:{qn.coordinates}, name:{qn.name}, id:{qn.id}.")
    



# data = []
# go_back = []
# for c, i in enumerate(jdata):
#     if 'education' in i.keys():
#         data.append(i['education'])
#         go_back.append(c)





#lsh.shing_minhash_lsh(data, k=3, C=100, B=50, threshold=0.35)




