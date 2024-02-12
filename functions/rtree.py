import math

# Represents a point or a cuboid in 3d space
class Node:
    # Give coordinates
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
    # Get min coordinates (min distance measured from (0,0,0))
    def getmin(self):
        return (self.minx,self.miny,self.minz)
    # Get max coordinates (max distance measured from (0,0,0))
    def getmax(self):
        return (self.maxx,self.maxy,self.maxz)

# Gets json data and returns a list with points as nodes
def get_nodelist(jdata):
    # From json records to nodes
    nodelist = []
    for num,i in enumerate(jdata):
        n1 = i['name'].split()[-1]   # Get surname from full name
        n2 = n1.ljust(4, 'a')[:4]   # Padding so it gets correct sorting place
        n = str_int.str_to_int(n2)   # Get a number value for the surname
        a = i['awards']
        d = i['dblp_records']
        nodelist.append(Node(n, a, d, n, a, d, id=num))
    # Get max values of each dimension
    tmaxx, tmaxy, tmaxz = (0,0,0)
    for i in nodelist:
        if i.maxx > tmaxx:
            tmaxx = i.maxx
        if i.maxy > tmaxy:
            tmaxy = i.maxy
        if i.maxz > tmaxz:
            tmaxz = i.maxz
    # Normalize nodes' coordinates
    for i in nodelist:
        i.minx, i.miny, i.minz = (i.minx/tmaxx, i.miny/tmaxy, i.minz/tmaxz)
        i.maxx, i.maxy, i.maxz = (i.maxx/tmaxx, i.maxy/tmaxy, i.maxz/tmaxz)

    return (nodelist, tmaxx, tmaxy, tmaxz)

# Get the Euclidean distance of 2 points in 3d space
def dist(xyz1, xyz2):
    return math.sqrt(math.pow(xyz1[0]-xyz2[0], 2) + 
                     math.pow(xyz1[1]-xyz2[1], 2) + 
                     math.pow(xyz1[2]-xyz2[2], 2))

# Get index of a point in nodelist that is nearest to the point with coordinates xyz
# xyz is like (x,y,z)
def nearest(xyz, nodelist):
    indx = 0
    for i in range(len(nodelist)):
        if (dist(nodelist[i].getmin(), xyz) < 
            dist(nodelist[indx].getmin(), xyz)):
            indx = i
    return indx

# Make a cuboid from nodes in nodelist
# Set the coordinates so that the cuboid encompases all the nodes
# Add to the cuboid's children the nodes of the nodelist
def makembr(nodelist):
    bignum = 100000000000
    mbr = Node(bignum,bignum,bignum,0,0,0)
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

# Give list with nodes-points. Get a list with the root node
def build(nodelist, K):
    nodes_for_mbr = nodelist   # List with nodes to put in MBRs
    list_with_mbrs = []   # List with final list with MBRs
    start = (0,0,0)

    if len(nodelist) == 1:
        return nodelist

    local_list = []   # Temporary storage for each MBR
    while len(nodes_for_mbr) > 0:
        # if we need to create an MBR
        if (len(local_list) == K-1) or (len(nodes_for_mbr) == 1):
            near_idx = nearest(start,nodes_for_mbr)
            near = nodes_for_mbr.pop(near_idx)
            local_list.append(near)

            new_node = makembr(local_list)
            list_with_mbrs.append(new_node)
            local_list = []
            start = (0,0,0)
        # if we want to append a node to nodelist for the next MBR
        else:
            near_idx = nearest(start,nodes_for_mbr)
            near = nodes_for_mbr.pop(near_idx)
            local_list.append(near)
            start = near.getmin()
    return build(list_with_mbrs, K)


def mbr_intersects_mbr(big_mbr, small_mbr):
    if ((
        (big_mbr.minx<=small_mbr.minx and big_mbr.maxx>=small_mbr.minx) or
        (big_mbr.maxx>=small_mbr.maxx and big_mbr.minx<=small_mbr.maxx) or
        (big_mbr.minx>=small_mbr.minx and big_mbr.maxx<=small_mbr.maxx)
        ) and (
        (big_mbr.miny<=small_mbr.miny and big_mbr.maxy>=small_mbr.miny) or
        (big_mbr.maxy>=small_mbr.maxy and big_mbr.miny<=small_mbr.maxy) or
        (big_mbr.miny>=small_mbr.miny and big_mbr.maxy<=small_mbr.maxy)
        ) and (
        (big_mbr.minz<=small_mbr.minz and big_mbr.maxz>=small_mbr.minz) or
        (big_mbr.maxz>=small_mbr.maxz and big_mbr.minz<=small_mbr.maxz) or
        (big_mbr.minz>=small_mbr.minz and big_mbr.maxz<=small_mbr.maxz)
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
                if mbr_intersects_mbr(Node(minx,miny,minz,maxx,maxy,maxz,0), i):
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


class Rtree:
    def __init__(self, jdata, K=5):
        (self.nodelist, self.tmaxx, self.tmaxy, self.tmaxz) = get_nodelist(jdata)
        self.K = K
    def build_tree(self):
        self.root = build(self.nodelist.copy(), self.K)

    def search(self, n1, n2, a, d1, d2):   # use: search("a","c",0,0,2)
        n1_ = str_int.str_to_int(n1.ljust(4, 'a')[:4])
        n2_ = str_int.str_to_int(n2.ljust(4, 'z')[:4])
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
    
    rr = Rtree(jdata)
    rr.build_tree()
    #rr.print_tree()
    n1 = "Aaa"
    n2 = "zzzzzzzzzz"
    a1 = 0
    d1 = 0
    d2 = 10000
    ids = rr.search(n1,n2,a1,d1,d2)
    print(len(ids))


else:
    from functions import str_int
