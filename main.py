from functions import k_d, quad#, range, rtree, str_int, lsh
import os, json
from timeit import default_timer as timer
from time import perf_counter

path = os.path.abspath(os.getcwd())
with open(path + "\\data\\out2.json", "r", encoding="utf-8") as f:
    jdata = json.load(f)

n1 = "a"
n2 = "z"
a1 = 4
d1 = 100
d2 = 200

# #tic = timer()
# t0 = perf_counter()
# rr = rtree.rtree(jdata)
# rr.build_tree()
# t1 = perf_counter()
# print(f"R-Tree construction time: {t1-t0}")

# t0 = perf_counter()
# ids = rr.search(n1,n2,a1,d1,d2)
# t1 = perf_counter()
# print(f"R-Tree query time: {t1-t0}\n")


# t0 = perf_counter()
# tree_range = range.RangeTree(jdata)
# t1 = perf_counter()
# print(f"Range Tree construction time: {t1-t0}")
# t0 = perf_counter()
# ids_range = tree_range.query_driver([n1,n2],[a1,None],[d1,d2])
# t1 = perf_counter()
# print(f"Range Tree query time: {t1-t0}\n")

# toc = timer()

t0 = perf_counter()
octree, max_x = quad.init_quadTree(jdata)
t1 = perf_counter()
print(f"Quad Tree construction time: {t1-t0}")

t0 = perf_counter()
ids_quad = octree.range_query(octree.root, [[a1,max_x],[d1,d2],[quad.str_to_int(n1, "a"),quad.str_to_int(n2, "z")]], [])
t1 = perf_counter()
print(f"Quad Tree query time: {t1-t0}\n")
print(len(ids_quad))



k_dtree = k_d.KDTree(jdata)
lower = {"name": n1.lower(), "dblp": d1, "awards": a1}
upper = {"name": n2.lower(), "dblp": d2, "awards": max_x}
result = k_dtree.rangeQuery(k_dtree.root, 0, upper, lower, [])
print(len(result))





# print(((ids.sort()==ids_range.sort()) and (ids_range.sort()==ids_quad.sort())))  # put kd ids

# def edu():
#     educations = []
#     for id in ids:
#         educations.append(jdata[id]["education"])

#     groups = lsh.shing_minhash_lsh(educations, k=3, C=100, B=50, threshold=0.3, plot_threshold=0)
#     print(groups)

#     similar_ids = []
#     for g in groups:
#         id_g = []
#         for i in g:
#             id_g.append(ids[i])
#         similar_ids.append(id_g)

#     #print(similar_ids)

#     for sids in similar_ids:
#         if len(sids)>20:
#             continue
#         for sid in sids:
#             print(jdata[sid]["education"]+"---------------")
#         print("")
