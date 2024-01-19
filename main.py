# Main python script

#from functions import functions.k-d.py, functions.quad.py, functions.range.py, functions.r.py, functions.lsh.py
from functions import quad, k_d#,lsh
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
print(f"(QuadTree-Build)ellapsed time: {toc-tic} sec")
#range query quadTree
ranges = [[0,max_x],[0,10000],[quad.str_to_int("e"),quad.str_to_int("x")]]
quad_nodes = []
tic = timer()
quad_nodes = octree.range_query(octree.root, ranges, quad_nodes)
tic = timer()
print(f"(QuadTree-RangeQuery)ellapsed time: {tic-toc} sec")
#end
print(len(quad_nodes))
# for qn in quad_nodes:
#     print(f"coordinates:{qn.coordinates}, name:{qn.name}, id:{qn.id}.")
    
k_dtree = k_d.KDTree(jdata)
lower = {"name": "e", "dblp": 0, "awards": 0}#input
upper = {"name": "x", "dblp": 10000, "awards": max_x}#input
result = k_dtree.rangeQuery(k_dtree.root, 0, upper, lower, [])
print(len(result)) 

# for r in result:
#         print(r) 
# data = []
# go_back = []
# for c, i in enumerate(jdata):
#     if 'education' in i.keys():
#         data.append(i['education'])
#         go_back.append(c)





#lsh.shing_minhash_lsh(data, k=3, C=100, B=50, threshold=0.35)




