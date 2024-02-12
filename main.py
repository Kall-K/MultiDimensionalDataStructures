from functions import kd_tree, quad_tree, range_tree, r_tree, lsh
from time import perf_counter
from matplotlib import pyplot as plt
import os, json, string, random
import pandas as pd


max_a = 0

#=========================================================================================

def build_trees(jdata):
    
    global max_a

    runtimes = {}
    trees = {}

    # R-Tree construction
    t0 = perf_counter()
    rr = r_tree.Rtree(jdata)
    rr.build_tree()
    t1 = perf_counter()
    runtimes["r_tree"] = t1-t0
    trees["r_tree"] = rr

    # Range-Tree construction
    t0 = perf_counter()
    trees["range_tree"] = range_tree.RangeTree(jdata)
    t1 = perf_counter()
    runtimes["range_tree"] = t1-t0

    # Quad-Tree construction
    t0 = perf_counter()
    trees["quad_tree"], max_a = quad_tree.init_quadTree(jdata)
    t1 = perf_counter()
    runtimes["quad_tree"] = t1-t0

    # Kd-Tree construction
    t0 = perf_counter()
    trees["kd_tree"] = kd_tree.KDTree(jdata)
    t1 = perf_counter()
    runtimes["kd_tree"] = t1-t0

    return trees, runtimes

#=========================================================================================

def query_all(trees, n1, n2, a1, d1, d2):
    
    runtimes = {}

    rr = trees["r_tree"]
    tree_range = trees["range_tree"]
    octree = trees["quad_tree"]
    k_dtree = trees["kd_tree"]


    # R-Tree query
    t0 = perf_counter()
    ids_rtree = rr.search(n1,n2,a1,d1,d2)
    t1 = perf_counter()
    runtimes["r_tree"] = t1-t0
    
    # Range Tree query
    t0 = perf_counter()
    ids_range = tree_range.query_driver([n1,n2],[a1,None],[d1,d2])
    t1 = perf_counter()
    runtimes["range_tree"] = t1-t0

    # Quad Tree query
    t0 = perf_counter()
    ids_quad = octree.range_query(octree.root, [[a1,max_a],[d1,d2],[quad_tree.str_to_int(n1, "a"),quad_tree.str_to_int(n2, "z")]], [])
    t1 = perf_counter()
    runtimes["quad_tree"] = t1-t0

    lower = {"name":n1, "dblp":d1, "awards":a1}
    upper = {"name":n2,"dblp":d2, "awards":max_a}
    t0 = perf_counter()
    ids_kd = k_dtree.rangeQuery(k_dtree.root, 0, upper, lower, [])
    t1 = perf_counter()
    runtimes["kd_tree"] = t1-t0

    assert ids_rtree.sort() == ids_range.sort(), "Range tree ids not equal to R-tree ids"
    assert ids_rtree.sort() == ids_quad.sort(), "Range tree ids not equal to R-tree ids"
    assert ids_rtree.sort() == ids_kd.sort(), "Range tree ids not equal to R-tree ids"

    return runtimes, ids_rtree

#=========================================================================================

def run_experiments(trees, num_of_experiments=10):
    #rtree, range, quad, kd
    runtimes = {"parameters": [], "ids": [], "r_tree": [], "range_tree": [], "quad_tree": [], "kd_tree": []}
    for _ in range(num_of_experiments):
        n1 = random.choice(string.ascii_lowercase)
        n2 = random.choice(n1 + string.ascii_lowercase.split(n1)[1])
        a1 = random.randint(0,15)
        d1 = random.randint(0,500)
        d2 = random.randint(d1,500)
        runtimes["parameters"].append({"n1": n1, "n2": n2, "a1": a1, "d1": d1, "d2": d2})
        query_times, ids = query_all(trees, n1, n2, a1, d1, d2)
        runtimes["ids"].append(ids)

        runtimes["r_tree"].append(query_times["r_tree"])
        runtimes["range_tree"].append(query_times["range_tree"])
        runtimes["quad_tree"].append(query_times["quad_tree"])
        runtimes["kd_tree"].append(query_times["kd_tree"])

    return runtimes

#=========================================================================================

def unique_range_query(trees):
    n1 = input("Give min name letter: ")
    n2 = input("Give max name letter: ")
    a1 = input("Give min awards number: ")
    d1 = input("Give min dblp record number: ")
    d2 = input("Give max dblp record number: ")

    return query_all(trees, n1, n2, int(a1), int(d1), int(d2))

#=========================================================================================

def lsh_run(ids):
    educations = []
    for id in ids:
        educations.append(jdata[id]["education"])

    groups = lsh.shing_minhash_lsh(educations, k=3, C=100, B=50, threshold=0.3, plot_threshold=0)

    similar_ids = []
    for g in groups:
        id_g = []
        for i in g:
            id_g.append(ids[i])
        similar_ids.append(id_g)

    with open("lsh.txt", "w") as f:
        for sids in similar_ids:
            if len(sids)>20:
                continue
            for sid in sids:
                f.write(str(sid)+": "+jdata[sid]["name"]+"\n")
            f.write("\n")

#=========================================================================================

if __name__ == "__main__":

    #Read data from json file
    jdata = None

    path = os.path.abspath(os.getcwd())
    with open(path + "\\data\\out2.json", "r", encoding="utf-8") as f:
        jdata = json.load(f)

    #Number of queries executed
    print("If you set num of range queries equal to 1 you give the inputs manually \notherwise the parameters are configured automatically.\n")
    num_experiments = int(input("Select the number of range queries to be executed: "))
    #Build trees
    trees, build_times = build_trees(jdata)

    if (num_experiments > 1):
        #Execute random queries
        result = run_experiments(trees, num_experiments)
        
        #Bar plot of average construction times
        data = {"R-Tree": build_times["r_tree"], "Range Tree": build_times["range_tree"], "Quad Tree": build_times["quad_tree"], "KD Tree": build_times["kd_tree"]}
        trees = list(data.keys())
        times = list(data.values())

        fig = plt.figure(figsize = (10, 5))

        # creating the bar plot
        plt.bar(trees, times, color ='maroon', width = 0.4)

        plt.xlabel("Tree")
        plt.ylabel("Time")
        plt.title("Average construction times for all trees")
    

        #Average query times for each tree
        r_time = sum(result["r_tree"])/num_experiments
        range_time = sum(result["range_tree"])/num_experiments
        quad_time = sum(result["quad_tree"])/num_experiments
        kd_time = sum(result["kd_tree"])/num_experiments

        print(f"Average R-Tree time: {r_time}")
        print(f"Average Range Tree time: {range_time}")
        print(f"Average Quad-Tree time: {quad_time}")
        print(f"Average KD-Tree time: {kd_time}")

        for i, t in enumerate(result["r_tree"]):
            print(f"Time of R-Tree for query {i}: {t}")

        #Bar plot of average times for queries
        data = {"R-Tree": r_time, "Range Tree": range_time, "Quad Tree": quad_time, "KD Tree": kd_time}
        trees = list(data.keys())
        times = list(data.values())

        fig = plt.figure(figsize = (10, 5))

        # creating the bar plot for queries
        plt.bar(trees, times, color ='maroon', width = 0.4)

        plt.xlabel("Tree")
        plt.ylabel("Time")
        plt.title("Average query times for all trees")
        plt.show()

        #Export times to excel
        excel_data = {"R-Tree": result["r_tree"], "Range Tree": result["range_tree"], "Quad Tree": result["quad_tree"], "KD Tree": result["kd_tree"]}
        df = pd.DataFrame(excel_data, index=list(range(num_experiments)))
        df.to_excel("query_times.xlsx", index_label="Query")

        #Export queries to excel
        excel_queries = {"n1": [], "n2": [], "a1": [], "d1": [], "d2": []}

        for query in result["parameters"]:
            for key, value in query.items():
                excel_queries[key].append(value)

        df_queries = pd.DataFrame(excel_queries, index=list(range(num_experiments)))
        df_queries.to_excel("queries.xlsx", index_label = "Query")
    elif (num_experiments == 1):
        times, ids = unique_range_query(trees)

        print(f"Average R-Tree time: {times['r_tree']}")
        print(f"Average Range Tree time: {times['range_tree']}")
        print(f"Average Quad-Tree time: {times['quad_tree']}")
        print(f"Average KD-Tree time: {times['kd_tree']}")

        lsh_run(ids)
    else: print("Invalid Input, Pls try again!")