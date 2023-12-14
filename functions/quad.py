import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import string

#this type of Node is the coordinates which separates the space in 4 equal quadrants
class Node1:
    def __init__(self, coordinates, children, half_val):
        self.coordinates = coordinates
        self.half_val = half_val
        self.children = children

#this type of Node is the coordinates which represents the data
class Node2:
    def __init__(self, coordinates, children, name):
        self.coordinates = coordinates
        self.children = children
        self.name = name

class Octree:
    #initialize octree with the first node i.e. root
    def __init__(self, root_coordinates, root_children, root_half_val):
        self.root = Node1(root_coordinates, root_children, root_half_val)
    
    def insert_node(self, parent, node):
        x, y, z = self.compare_nodes(parent, node)
        pos = self.find_position(x, y, z)
        check = self.check_node_children(parent, pos)

        if check:
            parent.children[pos] = node
        else:
            child = parent.children[pos]
            flag = 0
            for n in child.children:
                if n != None: flag = 1

            if flag:
                #is a Node of type 1
                new_parent = parent.children[pos]
                self.insert_node(new_parent, node)
            else: 
                #is a Node of type 2
                new_parent = self.replace(parent, pos)
                parent.children[pos] = new_parent
                self.insert_direct(new_parent, child)
                self.insert_node(new_parent, node)

    def insert_direct(self, parent, node):
        x, y, z = self.compare_nodes(parent, node)
        pos = self.find_position(x, y, z)
        parent.children[pos] = node

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
        
        return Node1((x_, y_, z_), [None]*8, (half_x, half_y, half_z))

    def compare_nodes(self, parent_node, child_node):
        compare_x = parent_node.coordinates[0] >= child_node.coordinates[0]
        compare_y = parent_node.coordinates[1] >= child_node.coordinates[1]
        compare_z = parent_node.coordinates[2] >= child_node.coordinates[2]

        return compare_x, compare_y, compare_z
    
    def check_node_children(self, node, position):
        if node.children[position] == None:
            return True
        
    #here i made a truth table and i found the expression to calculate the right position of the node
    def find_position(self, co_x, co_y, co_z):
        return 4*int((not co_z))+2*int((not co_y))+int((co_x ^ co_y))
    
    def traverse(self, node):
        if hasattr(node, "name"):
            print(node.coordinates, node.name)
        else:print(node.coordinates)
        for n in node.children:
            if n != None:
                self.traverse(n)

#function to transform name(string) to number 
def letter_to_int(str1):
    let = string.ascii_lowercase
    for i in range(len(let)):
        if let[i] == str1:
            return i+1

def str_to_int(word):
    word = word.lower()
    word = word.replace(" ", "")[:10]
    num = 0
  
    word = word[::-1]
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



if __name__ == "__main__":
    file_path = './data/out.json'

    with open(file_path, 'r', encoding='UTF8') as file:
        data = json.load(file)
    
    nodes = []
    max_x = 0
    max_y = 0
    max_z = 0
    min_z = 1e+16
    counter_data = 0
    fig = plt.figure()     
    ax = fig.add_subplot(111, projection='3d')
    for i in data: 
        name_val = str_to_int(i["name"])
        nodes.append(Node2(tuple([i["awards"],i["dblp_records"],name_val]), [None]*8, i["name"])) 

        if i["awards"]>max_x:
            max_x = i["awards"]
        if i["dblp_records"]>max_y:
            max_y = i["dblp_records"]
        if name_val>=max_z:
            max_z = name_val
        if name_val<=min_z:
            min_z = name_val
            
        ax.scatter(i["awards"],i["dblp_records"], name_val)
        

    octree = Octree((max_x/2, max_y/2, (max_z-min_z)/2), [None]*8, (max_x/4,max_y/4,(max_z-min_z)/4))
    plot_3d_lines(ax, max_x/2, max_y/2, (max_z-min_z)/2, max_x/4,max_y/4,(max_z-min_z)/4)
     

    for n in nodes:        
        octree.insert_node(octree.root, n)
        counter_data +=1
    
    print(counter_data)
        
    #octree.traverse(octree.root)

    ax.set_xlabel('awards')
    ax.set_ylabel('dblp-record')
    ax.set_zlabel('name')
    plt.show()


