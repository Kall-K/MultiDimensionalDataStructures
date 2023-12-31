import os, json, random


k = 3   # for shingling
C = 100   # number of hash functions for minhashing
B = 50   # number of buckets for hash functions for lsh
threshold = 0.35   # similarity threshold

path = os.path.abspath(os.getcwd())
end1 = "\\..\\data\\out2.json"
end2 = "\\data\\out2.json"
with open(path + end2, "r", encoding="utf-8") as f:
    jdata = json.load(f)

data = []
go_back = []
for c, i in enumerate(jdata):
    if 'education' in i.keys():
        data.append(i['education'])
        go_back.append(c)


#data = ['abcdefgeggerdhaha', 'abcdefgkaggerdhaha']

def find_b(C, t):
    bs = []
    for b in range(1,C):
        if C%b==0:
            bs.append(b)
    b = -1
    for i in bs:
        if abs((1/b)**(b/C)-t)>abs((1/i)**(i/C)-t):
            b = i
    return b


def shingling(string, k):
    flist = []
    for i in range(len(string)-k+1):
        if string[i:i+k] not in flist:
            flist.append(string[i:i+k])
    return flist


def shingle(data, k):
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

# from data to signatures
def get_signatures(data, k, C):
    shingled_data = shingle(data,k)
    all_shingles = get_shingles(shingled_data)
    t = make_table(all_shingles, shingled_data)
    sig = minhash(t,C)
    return sig


def compare_sig(sig1, sig2):
    counter = 0
    for i in range(len(sig1)):
        if sig1[i]==sig2[i]:
            counter += 1
    return counter/len(sig1)

def int_sig(sig):
    fstr = ''
    for i in sig:
        fstr+=str(int(i))
    return int(fstr)

def lsh(data, k, C, b, B, threshold):
    r = int(C/b)
    sig = get_signatures(data,k,C)

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
            buckets[h2(int_sig(sign), B)].append(j)

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



b = find_b(C,threshold)
l = lsh(data,k,C,b,B,threshold)
for group in l:
    for s in group:
        print(jdata[go_back[s]]['name'])
    print('')



