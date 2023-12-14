import json
import matplotlib.pyplot as plt

# Implementatoin of quadtree. It doesnt work for the case where to point have the same coordinates#


#this type of Node is the coordinates which separates the space in 4 equal quadrants
class Node1:
    def __init__(self, coordinates, children, half_val):
        self.coordinates = coordinates
        self.half_val = half_val
        self.children = children

#this type of Node is the coordinates which represents the data
class Node2:
    def __init__(self, coordinates, children):
        self.coordinates = coordinates
        self.children = children

class Octree:
    #initialize octree with the first node i.e. root
    def __init__(self, root_coordinates, root_children, root_half_val):
        self.root = Node1(root_coordinates, root_children, root_half_val)
    
    def insert_node(self, parent, node):
        x, y = self.compare_nodes(parent, node)#
        pos = self.find_position(x, y)#
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
        x, y = self.compare_nodes(parent, node)
        pos = self.find_position(x, y)
        parent.children[pos] = node

    def replace(self, node, position):#
        a = b = 1 

        if position in [0,3]:
            a = -1
        if position in [0,1]:
            b = -1      

        x_ = node.coordinates[0]+(a*node.half_val[0])
        y_ = node.coordinates[1]+(b*node.half_val[1])
        # match position:
        #     case 0:
        #         x_ = node.coordinates[0]-node.half_val[0]
        #         y_ = node.coordinates[1]-node.half_val[1]
        #     case 1:
        #         x_ = node.coordinates[0]+node.half_val[0]
        #         y_ = node.coordinates[1]-node.half_val[1]
        #     case 2:
        #         x_ = node.coordinates[0]+node.half_val[0]
        #         y_ = node.coordinates[1]+node.half_val[1]
        #     case 3:
        #         x_ = node.coordinates[0]-node.half_val[0]
        #         y_ = node.coordinates[1]+node.half_val[1]
        #     case _:
        #         print("Invalid node position")

        half_x = node.half_val[0]/2
        half_y = node.half_val[1]/2
        #
        plt.vlines(x_, y_-(2*half_y), y_+(2*half_y), colors='gray', alpha=0.5)
        plt.hlines(y_, x_-(2*half_x), x_+(2*half_x), colors='gray', alpha=0.5)
        #
        return Node1((x_, y_), [None]*4, (half_x, half_y))

    def compare_nodes(self, parent_node, child_node):#
        compare_x = parent_node.coordinates[0] >= child_node.coordinates[0]
        compare_y = parent_node.coordinates[1] >= child_node.coordinates[1]

        return compare_x, compare_y
    
    def check_node_children(self, node, position):
        if node.children[position] == None:
            return True

    def find_position(self, co_x, co_y):#
        return 2*int((not co_y))+int((co_x ^ co_y))
        # if co_x and co_y:
        #     return 0
        # elif co_x and not co_y:
        #     return 3
        # elif not co_x and co_y:
        #     return 1
        # else:
        #     return 2
 
    def traverse(self, node):
        print(node.coordinates)
        for n in node.children:
            if n != None:
                self.traverse(n)


if __name__ == "__main__":
    file_path = './data/out.json'

    with open(file_path, 'r', encoding='UTF8') as file:
        data = json.load(file)
    
    nodes = []
    max_x = 0
    max_y = 0
    counter_data = 0
    for i in data: 
        nodes.append(Node2(tuple([i["awards"],i["dblp_records"]]), [None]*4)) 
        if i["awards"]>max_x:
            max_x = i["awards"]
        if i["dblp_records"]>max_y:
            max_y = i["dblp_records"]
        #
        plt.scatter(i["awards"],i["dblp_records"])
        #

    octree = Octree((max_x/2, max_y/2), [None]*4, (max_x/4,max_y/4))
    #
    plt.vlines(7.5, 552-(2*276), 552+(2*276), colors='gray', alpha=0.5)
    plt.hlines(552, 7.5-(2*3.75), 7.5+(2*3.75), colors='gray', alpha=0.5)
    # 


    for n in nodes:
        octree.insert_node(octree.root, n)
        #
        counter_data +=1
    
    print(counter_data)
        #
   
    #octree.traverse(octree.root)


    plt.xlabel('awards')
    plt.ylabel('dblps')
    plt.show()

