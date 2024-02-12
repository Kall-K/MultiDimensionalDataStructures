import random

# Find best b so that the threshold is close to t
def find_b(C, t):
    bs = []
    for b in range(1,C):
        if C%b==0:
            bs.append(b)
    b = -1
    for i in bs:
        if abs((1/b)**(b/C)-t) > abs((1/i)**(i/C)-t):
            b = i
    return b


def plot_t(t, b, C):
    import matplotlib.pyplot as plt

    x1, y1 = ([t, t], [0, 1])
    t_aprox = (1/b)**(b/C)
    x2, y2 = ([t_aprox, t_aprox], [0, 1])

    x3, y3 = ([],[])
    for j in range(0,11,1):
        i = j/10
        x3.append(i)
        y3.append(1-(1-i**(C/b))**b)

    plt.plot(x1, y1, label='threshold')
    plt.plot(x2, y2, label='threshold aproximation')
    plt.plot(x3, y3, marker = 'o')
    plt.legend()
    plt.xlabel('Jacard similarity of 2 sets')
    plt.ylabel('Probability of sharing a bucket')
    plt.show()


def shingling(string, k):
    flist = []
    for i in range(len(string)-k+1):
        if string[i:i+k] not in flist:
            flist.append(string[i:i+k])
    return flist


def shingle_data(data, k):
    shingled_data = []
    for i in data:
        shingled_data.append(shingling(i, k))
    return shingled_data


def get_shingles(shingled_data):
    all_shingles = []
    for i in shingled_data:
        for j in i:
            if j not in all_shingles:
                all_shingles.append(j)
    return all_shingles


def make_table(all_shingles, shingled_data):
    table = []
    for sset in shingled_data:
        column = []
        for sh in all_shingles:
            if sh in sset:
                column.append(1)
            else:
                column.append(0)
        table.append(column)
    return table

# from data to signatures
def get_shingle_table(data, k):
    shingled_data = shingle_data(data,k)
    all_shingles = get_shingles(shingled_data)
    t = make_table(all_shingles, shingled_data)
    return t


def h(seed, num, t_len):
    return ((seed+1)*(num+10) + seed + t_len/2)%t_len


def h2(seed, buckets):
    random.seed(seed*100 + 10)
    return round(random.random()*100*(buckets + 100))%buckets


def minhash(table, C):
    M = []
    for i in range(len(table)):
        M.append([])
        for j in range(C):
            M[i].append(len(table[0])+1)

    for r in range(len(table[0])):
        for c in range(len(table)):
            if table[c][r]==1:
                for i in range(C):
                    if h(i,r,len(table[0])) < M[c][i]:
                        M[c][i] = h(i,r,len(table[0]))
    return M


def compare_sig(sig1, sig2):
    counter = 0
    for i in range(len(sig1)):
        if sig1[i]==sig2[i]:
            counter += 1
    return counter/len(sig1)


def sig2int(sig):
    fstr = ''
    for i in sig:
        fstr+=str(int(i))
    return int(fstr)


def lsh(sig, C, b, B, threshold):
    r = int(C/b)

    bands = []
    for i in range(b):
        band = []
        for j in range(len(sig)):
            band.append(sig[j][i*r:i*r+r])
        bands.append(band)

    groups = []
    for band in bands:
        buckets = []
        for i in range(B):
            buckets.append([])
        for j,sign in enumerate(band):
            buckets[h2(sig2int(sign), B)].append(j)

        for bucket in buckets:
            if len(bucket) < 2:
                continue

            sig1 = bucket[0]
            group = []
            for sig_no in bucket:
                if compare_sig(sig[sig1], sig[sig_no]) > threshold:
                    group.append(sig_no)
            if len(group)>1:
                groups.append(group)

    return groups


def get_unique_groups(groups):
    unique_groups = []
    for group in groups:
        unique = 1
        for u in unique_groups:
            if sorted(group)==sorted(u):
                unique = 0
        if unique:
            unique_groups.append(group)
    return unique_groups


def shing_minhash_lsh(data, k, C, B, threshold, plot_threshold=1):
    # k: for shingling
    # C: number of hash functions for minhashing
    # B: number of buckets for hash functions for lsh
    # threshold: similarity threshold

    t = get_shingle_table(data, k)   # Get table with samples(columns) and shingles(rows)
    sig_with_minhash = minhash(t,C)   # Get table with samples(columns) and signatures(rows)

    b = find_b(C,threshold)   # Find b to satisfy threshold

    if plot_threshold:
        plot_t(threshold,b,C)
    
    groups = lsh(sig_with_minhash, C, b, B, threshold)   # Find similar groups

    groups_unique = get_unique_groups(groups)

    return groups_unique


if __name__ == "__main__":
    import os, json
    path = os.path.abspath(os.getcwd())
    end1 = "\\..\\data\\out2.json"
    end2 = "\\data\\out2.json"
    with open(path + end2, "r", encoding="utf-8") as f:
        jdata = json.load(f)

    data = []
    for i in jdata:
        if 'education' in i.keys():
            data.append(i['education'])

    groups = shing_minhash_lsh(data, k=3, C=100, B=50, threshold=0.4, plot_threshold=0)
    for group in groups:
        if len(group)>10:
            continue
        for s in group:
            print(jdata[s]['name'])
        print('')
    #print(groups)

