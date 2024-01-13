import math

class node:
    def __init__(self, minx, miny, minz, maxx, maxy, maxz, id=None):
        self.minx = minx
        self.miny = miny
        self.minz = minz
        self.maxx = maxx
        self.maxy = maxy
        self.maxz = maxz
        self.id = id
        if id == None:
            self.children = []
    def getmin(self):
        return (self.minx,self.miny,self.minz)
    def getmax(self):
        return (self.maxx,self.maxy,self.maxz)


def get_nodelist(jdata):
    nodelist = []
    for num,i in enumerate(jdata):
        n1 = i['name'].split()[-1]
        n2 = n1.ljust(4, 'a')[:4]
        n = str_int.str_to_int(n2)
        a = i['awards']
        d = i['dblp_records']
        nodelist.append(node(n, a, d, n, a, d, id=num))

    tmaxx, tmaxy, tmaxz = (0,0,0)
    for i in nodelist:
        if i.maxx > tmaxx:
            tmaxx = i.maxx
        if i.maxy > tmaxy:
            tmaxy = i.maxy
        if i.maxz > tmaxz:
            tmaxz = i.maxz
    for i in nodelist:
        i.minx, i.miny, i.minz = (i.minx/tmaxx, i.miny/tmaxy, i.minz/tmaxz)
        i.maxx, i.maxy, i.maxz = (i.maxx/tmaxx, i.maxy/tmaxy, i.maxz/tmaxz)

    return (nodelist, tmaxx, tmaxy, tmaxz)


def dist(xyz1, xyz2):
    return math.sqrt(math.pow(xyz1[0]-xyz2[0], 2) + 
                     math.pow(xyz1[1]-xyz2[1], 2) + 
                     math.pow(xyz1[2]-xyz2[2], 2))

def nearest(xyz, nodelist):
    indx = 0
    for i in range(len(nodelist)):
        if (dist(nodelist[i].getmin(), xyz) < 
            dist(nodelist[indx].getmin(), xyz)):
            indx = i
    return indx

def makembr(nodelist):
    bignum = 100000000000
    mbr = node(bignum,bignum,bignum,0,0,0)
    for i in nodelist:
        if i.minx < mbr.minx:
            mbr.minx = i.minx
        if i.miny < mbr.miny:
            mbr.miny = i.miny
        if i.minz < mbr.minz:
            mbr.minz = i.minz
        if i.maxx > mbr.maxx:
            mbr.maxx = i.maxx
        if i.maxy > mbr.maxy:
            mbr.maxy = i.maxy
        if i.maxz > mbr.maxz:
            mbr.maxz = i.maxz
    for i in nodelist:
        mbr.children.append(i)
    return mbr

def build(list1, K):
    list2 = list1
    list3 = []
    start = (0,0,0)

    if len(list1) == 1:
        return list1

    llist = []
    while len(list2)>0:
        if (len(llist) == K-1) or (len(list2) == 1):
            near_idx = nearest(start,list2)
            near = list2.pop(near_idx)
            llist.append(near)
            start = near.getmin()

            new_node = makembr(llist)
            list3.append(new_node)
            llist = []
            start = (0,0,0)
        else:
            near_idx = nearest(start,list2)
            near = list2.pop(near_idx)
            llist.append(near)
            start = near.getmin()
    return build(list3, K)


def inters(n1, range):
    if ((
        (range.minx<=n1.minx and range.maxx>=n1.minx) or
        (range.maxx>=n1.maxx and range.minx<=n1.maxx) or
        (range.minx>=n1.minx and range.maxx<=n1.maxx)
        ) and (
        (range.miny<=n1.miny and range.maxy>=n1.miny) or
        (range.maxy>=n1.maxy and range.miny<=n1.maxy) or
        (range.miny>=n1.miny and range.maxy<=n1.maxy)
        ) and (
        (range.minz<=n1.minz and range.maxz>=n1.minz) or
        (range.maxz>=n1.maxz and range.minz<=n1.maxz) or
        (range.minz>=n1.minz and range.maxz<=n1.maxz)
        )):
        return 1
    return 0

def get_results(root,minx=0,miny=0,minz=0,maxx=1,maxy=1,maxz=1):
    results = []
    def search(root,minx,miny,minz,maxx,maxy,maxz):
        for i in root:
            if i.id != None:
                if ((i.minx>=minx) and (i.miny>=miny) and (i.minz>=minz) and
                    (i.minx<=maxx) and (i.miny<=maxy) and (i.minz<=maxz)):
                    results.append(i.id)
            else:
                if inters(i, node(minx,miny,minz,maxx,maxy,maxz,0)):
                    search(i.children, minx,miny,minz,maxx,maxy,maxz)

    search(root,minx,miny,minz,maxx,maxy,maxz)
    return results


def printdata(data, root, show_points=0, show_rects=2):
    """
    show_rects: if 0 it will NOT show rects,
                if 1 it will show ALL rects,
                if 2 it will show final rects
    """
    import matplotlib.pyplot as plt

    ax = plt.figure().add_subplot(projection='3d')

    # Plot points
    xs, ys, zs = ([], [], [])
    for i in data:
        xs.append(i.minx)
        xs.append(i.maxx)
        ys.append(i.miny)
        ys.append(i.maxy)
        zs.append(i.minz)
        zs.append(i.maxz)
    if show_points:
        ax.scatter(xs, ys, zs)

    # Plot rectangles
    def plot_rect_xyz(cmin=(0,0,0), cmax=(1,1,1)):
        x = [cmin[0], cmax[0], cmax[0], cmin[0], cmin[0],   cmin[0],   cmin[0], cmax[0], cmax[0], cmin[0], cmin[0],    cmax[0], cmax[0],    cmax[0], cmax[0],   cmin[0], cmin[0]]
        y = [cmin[1], cmin[1], cmax[1], cmax[1], cmin[1],   cmin[1],   cmin[1], cmin[1], cmax[1], cmax[1], cmin[1],    cmin[1], cmin[1],    cmax[1], cmax[1],   cmax[1], cmax[1]]
        z = [cmin[2], cmin[2], cmin[2], cmin[2], cmin[2],   cmax[2],   cmax[2], cmax[2], cmax[2], cmax[2], cmax[2],    cmax[2], cmin[2],    cmin[2], cmax[2],   cmax[2], cmin[2]]
        return [x,y,z]
    
    rect_list = []
    def get_rects(root):
        if show_rects==1:
            for i in root:
                if i.id == None:
                    rect_list.append([i.getmin(), i.getmax()])
                    get_rects(i.children)
        else:
            for i in root:
                if i.id == None:
                    if i.children[0].id != None:
                        rect_list.append([i.getmin(), i.getmax()])
                    get_rects(i.children)
    
    if show_rects > 0:
        get_rects(root)
        for i in rect_list:
            x,y,z = plot_rect_xyz(i[0],i[1])
            ax.plot(x, y, z, zdir='z')

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()


def main_tree(jdata, K=100, mode='search'):
    (nodelist, tmaxx, tmaxy, tmaxz) = get_nodelist(jdata)
    root = build(nodelist.copy(), K)

    if mode=='search':
        n1 = input("Give the start of the range for names: ")
        n1 = str_int.str_to_int(n1.ljust(4, 'a')[:4])
        n2 = input("Give the end of the range for names: ")
        n2 = str_int.str_to_int(n2.ljust(4, 'a')[:4])

        a = int(input("Give the award threshold number: "))
        d1 = int(input("Give the start of the range for dblp: "))
        d2 = int(input("Give the end of the range for dblp: "))

        res = get_results(root, minx=n1/tmaxx, miny=a/tmaxy, minz=d1/tmaxz, maxx=n2/tmaxx, maxz=d2/tmaxz)
        print("Number of results: " + str(len(res)))
        
        if input("show? ")=="y":
            for i in res:
                print(i)
        
        return res

    elif mode=='print':
        printdata(nodelist, root)

#main_tree(jdata)

class rtree:
    def __init__(self, jdata, K=5):
        (self.nodelist, self.tmaxx, self.tmaxy, self.tmaxz) = get_nodelist(jdata)
        self.K = K
    def build_tree(self):
        self.root = build(self.nodelist.copy(), self.K)

    def search(self, n1, n2, a, d1, d2):
        n1_ = str_int.str_to_int(n1.ljust(4, 'a')[:4])
        n2_ = str_int.str_to_int(n2.ljust(4, 'a')[:4])
        return get_results(self.root, minx=n1_/self.tmaxx, miny=a/self.tmaxy,
                    minz=d1/self.tmaxz, maxx=n2_/self.tmaxx, maxz=d2/self.tmaxz)
    def print_tree(self):
        printdata(self.nodelist, self.root)

if __name__ == "__main__":
    import os, json
    import str_int

    path = os.path.abspath(os.getcwd())
    end1 = "\\..\\data\\out2.json"
    end2 = "\\data\\out2.json"
    with open(path + end2, "r", encoding="utf-8") as f:
        jdata = json.load(f)
    
    rr = rtree(jdata)
    rr.build_tree()
    rr.print_tree()

else:
    from functions import str_int
