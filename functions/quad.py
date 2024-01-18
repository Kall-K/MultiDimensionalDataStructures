import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import string
import re

fig = plt.figure()     
ax = fig.add_subplot(111, projection='3d')

#this type of Node is the coordinates which separates the space in 4 equal cubes
class Node1:
    def __init__(self, coordinates, children, half_val):
        self.coordinates = coordinates
        self.half_val = half_val
        self.children = children

#this type of Node is the coordinates which represents the data
class Node2:
    def __init__(self, coordinates, name, id):
        self.coordinates = coordinates
        self.name = name
        self.id = id

class Octree:
    #initialize octree with the first node i.e. root
    def __init__(self, root_coordinates, root_children, root_half_val):
        self.root = Node1(root_coordinates, root_children, root_half_val)
    
    def insert_node(self, parent, node):
        x, y, z = self.compare_nodes(parent, node)
        pos = self.find_position(x, y, z)
        check, p = self.check_node_children(parent, pos)

        if check:
            parent.children[pos][p] = node
        else:
            child = parent.children[pos]
            flag = 0
            
            if len(child) == 1: flag = 1

            if flag:
                #is a Node of type 1
                new_parent = parent.children[pos][0]
                self.insert_node(new_parent, node)
            else: 
                #is a Node of type 2
                new_parent = self.replace(parent, pos)
                parent.children[pos] = []
                parent.children[pos].append(new_parent)
                for n in child:
                    self.insert_node(new_parent, n)
                self.insert_node(new_parent, node)

    #create new point to separate space in equal-cubes
    def replace(self, node, position):
        a = b = c = 1
        if position in [0,3,4,7]:
            a = -1
        if position in [0,1,4,5]:
            b = -1
        if position in [0,1,2,3]:
            c = -1       

        x_ = node.coordinates[0]+(a*node.half_val[0])
        y_ = node.coordinates[1]+(b*node.half_val[1])
        z_ = node.coordinates[2]+(c*node.half_val[2])

        half_x = node.half_val[0]/2
        half_y = node.half_val[1]/2
        half_z = node.half_val[2]/2

        plot_3d_lines(ax, x_, y_, z_, half_x, half_y, half_z)
        
        return Node1((x_, y_, z_), [[None]*9 for _ in range(8)], (half_x, half_y, half_z))

    def compare_nodes(self, parent_node, child_node):
        compare_x = parent_node.coordinates[0] >= child_node.coordinates[0]
        compare_y = parent_node.coordinates[1] >= child_node.coordinates[1]
        compare_z = parent_node.coordinates[2] >= child_node.coordinates[2]

        return compare_x, compare_y, compare_z
    
    #if the node hasnt child in the given position function returns True
    def check_node_children(self, parent, position):
        for i in range(len(parent.children[position])):
            if parent.children[position][i] == None:
                return True, i

        return False, -1
        
    #here i made a truth table and i found the expression to calculate the right position of the node
    def find_position(self, co_x, co_y, co_z):
        return 4*int((not co_z))+2*int((not co_y))+int((co_x ^ co_y))
    
    #traverse tree
    def traverse(self, node):
        print(node.coordinates,"->parent")
        for n in node.children:
            for i in range(len(n)):
                if hasattr(n[i], "children"): 
                    self.traverse(n[i])
                elif n[i] != None: 
                    print(f"coordinates:{n[i].coordinates}, name:{n[i].name}, id:{n[i].id}.")
    
    #range query
    def range_query(self, node, ranges, selected_nodes):
        pp = []
        pp = self.possible_pos(node, ranges)
        for p in pp:
            if node.children[p] !=None:
                if len(node.children[p]) == 1 :
                    self.range_query(node.children[p][0], ranges, selected_nodes)
                else:
                    for i in range(len(node.children[p])):
                        if self.node_in_range(node.children[p][i], ranges):
                            selected_nodes.append(node.children[p][i].id)
                           
        return selected_nodes

    def node_in_range(self, node, ranges):
        val = 0
        
        if node != None:
            for i in range(3):
                if  ranges[i][0] <= node.coordinates[i] <= ranges[i][1]:
                    val += 1
            if val == 3:
                return True
        
    def possible_pos(self, node, ranges):
        val_xL = node.coordinates[0]>=ranges[0][0] # x: area Left pos = 0,3,4,7
        val_xR = node.coordinates[0]<ranges[0][1] # x: area Right pos = 1,2,4,6
        if val_xL and val_xR: set_x = {0,1,2,3,4,5,6,7}
        elif val_xL: set_x = {0,3,4,7}
        elif val_xR: set_x = {1,2,4,6}

        val_yF = node.coordinates[1]>=ranges[1][0] # y: area Front pos = 0,1,4,5
        val_yB = node.coordinates[1]<ranges[1][1] # y: area Back pos = 2,3,6,7
        if val_yF and val_yB: set_y = {0,1,2,3,4,5,6,7}
        elif val_yF: set_y = {0,1,4,5}
        elif val_yB: set_y = {2,3,6,7}

        val_zD = node.coordinates[2]>=ranges[2][0] # z: area Down pos = 0,1,2,3
        val_zU = node.coordinates[2]<ranges[2][1] # z: area Up pos = 4,5,6,7
        if val_zD and val_zU: set_z = {0,1,2,3,4,5,6,7}
        elif val_zD: set_z = {0,1,2,3}
        elif val_zU: set_z = {4,5,6,7}

        return list(set_x.intersection(set_y, set_z))
#end of class octree

#functions to transform name(string) to number 
def letter_to_int(str1):  
    let = string.ascii_lowercase
    for i in range(len(let)):
        if let[i] == str1:
            return i    #or i+1

def str_to_int(word):
    word = word.lower()
    word = word.split()[-1]
    word = re.sub(r'[^a-z]+', '', word)
    l=4
    if len(word) < l:
        for i in range(l-len(word)):
            word += "a"
    if len(word) >= l:
        word = word[0:l]
    word = word[::-1]

    num = 0
    pow = 0
    for i in range(len(word)):
        if word[i] not in string.ascii_lowercase:
            continue
        num += letter_to_int(word[i])*(26**pow)
        pow += 1
    return num

#create 3d lines 
def plot_3d_lines(ax, x, y, z, half_x, half_y, half_z):
    ax.plot([x-2*half_x, x+2*half_x], [y, y], [z, z], color='red', alpha=0.5)
    ax.plot([x, x], [y-2*half_y, y+2*half_y], [z, z], color='green', alpha=0.5)
    ax.plot([x, x], [y, y], [z-2*half_z, z+2*half_z], color='blue', alpha=0.5)

def init_quadTree(data):
    #x->awards y->dblp_records z->name
    nodes = []
    max_x = max_y = max_z = 0
    min_z = 1e+13
    #consider that min of x and y is 0

    for index, value in enumerate(data): 
        name_val = str_to_int(value["name"])
        nodes.append(Node2(tuple([value["awards"],value["dblp_records"],name_val]), value["name"], index))  

        if value["awards"]>max_x:
            max_x = value["awards"]
        if value["dblp_records"]>max_y:
            max_y = value["dblp_records"]
        if name_val>=max_z:
            max_z = name_val
        if name_val<=min_z:
            min_z = name_val
            
        ax.scatter(value["awards"],value["dblp_records"], name_val)
   

    octree = Octree((max_x/2, max_y/2, min_z+(max_z-min_z)/2), [[None]*9 for _ in range(8)], (max_x/4,max_y/4,(max_z-min_z)/4))
    plot_3d_lines(ax, max_x/2, max_y/2, min_z+(max_z-min_z)/2, max_x/4,max_y/4,(max_z-min_z)/4)
     
    #insert points in quadtree
    counter_data = 0
    for n in nodes:        
        octree.insert_node(octree.root, n)
        
        counter_data +=1
    #
    #print(counter_data)
    #

    return octree, max_x


if __name__ == "__main__":
    file_path = './data/out2.json'

    with open(file_path, 'r', encoding='UTF8') as file:
        data = json.load(file)

    octree, max_x = init_quadTree(data)

    #print tree
    #octree.traverse(octree.root)

    #range query
    ranges = [[0,max_x],[0,10000],[str_to_int("a"),str_to_int("z")]]
    selected_nodes = []
    selected_nodes = octree.range_query(octree.root, ranges, selected_nodes)
    
    for sn in selected_nodes:
        print(sn)
        #print(f"coordinates:{sn.coordinates}, name:{sn.name}, id:{sn.id}.")

    print(len(selected_nodes))

    #plot
    ax.set_xlabel('awards')
    ax.set_ylabel('dblp-record')
    ax.set_zlabel('name')
    #plt.show()



