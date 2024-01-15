import json
from typing import Any

index = {3: "name", 2: "awards", 1: "dblp"}

#d = {3: "name", 2: "awards", 1: "dblp"}

#================================================================================================

class DataPoint:

    def __init__(self, name: str, awards: int, dblp: int, education: str, id: int):
        self.data = {"name": name, "awards": awards, "dblp": dblp, "education": education, "id": id}

    def __getattr__(self, name: str) -> Any:
        val = self.data.get(name, None)

        if val is None:
            raise AttributeError
        
        return self.data[name]
    
    def __str__(self):
        return f"Name: {self.name}\nAwards: {self.awards}\nDBLP: {self.dblp}\n"
    
    def __getitem__(self, key: str):
        return self.data[key]
    
#================================================================================================

class RangeTreeNode:

    def __init__(self, value, data, parent = None, left = None, right = None):
        self.left = left
        self.right = right

        self.data = data
        self.value = value

        self.alt_tree: RangeTree = None

        #AVL Stuff
        self.parent = parent
        self.height = 0
        self.hb = 0

    def __str__(self):
        return f"Address: {id(self)}\nValue: {self.data}"
    
#================================================================================================
    
class RangeTree:
    '''
    dataset: Path to the json file containing the dataset
    '''

    def __init__(self, dataset, dimension = 3):    
        self.dataset = dataset
        self.root = None
        self.dimension = dimension

        if self.dimension == 3: #Create tree from JSON file
            #Get the dataset as a JSON object

            for i, scientist in enumerate(dataset):
                self.insert(
                DataPoint(
                    scientist["name"],
                    scientist["awards"],
                    scientist["dblp_records"],
                    scientist.get("education", "EMPTY"),
                    i
                ))
        else: #Create tree using existing data in the dataset list
            for data_point in dataset:
                self.insert(data_point)

        if dimension > 1:
            self.create_alt_trees(self.root)

    #================================================================================================

    def create_alt_trees(self, node):
        
        if node.left is None:
            data = node.data
            node.alt_tree = RangeTree(data, self.dimension - 1)
            node.data = None
            return data
        
        leaves = []
        
        leaves = leaves + self.create_alt_trees(node.left)
        leaves = leaves + self.create_alt_trees(node.right)

        node.alt_tree = RangeTree(leaves, self.dimension - 1)
        
        return leaves

    #================================================================================================

    def search(self, search_value,  start_node = None, report = None) -> RangeTreeNode:
        '''
        Arguments:
            - search_value: The value to search for
            - start_node: Subtree where the search begins. Set None for root
            - report: Report subtrees in the search path. Either "left" or "right". 

        Returns:
            node: The tree node where the search ended
        '''
        if start_node == None:
            start_node = self.root

        if type(search_value) is str:
            search_value = search_value.lower()

        path = []
        current_node = start_node

        if start_node is not None:
            while current_node.left is not None:
                if search_value <= current_node.value:
                    if report == "right":
                        path.insert(0, current_node.right)
                    current_node = current_node.left
                else:
                    if report == "left":
                        path.append(current_node.left)
                    current_node = current_node.right

        if report is None:
            return current_node
        else:
            return current_node, path
        
    #================================================================================================
        
    def find_smallest(self) -> RangeTreeNode:
        '''
        Returns the node with the smallest value in the search tree
        '''

        current_node = self.root

        while current_node.left is not None:
            current_node = current_node.left

        return current_node
    
    #================================================================================================
        
    def find_biggest(self) -> RangeTreeNode:
        '''
        Returns the node with the biggest value in the search tree
        '''

        current_node = self.root

        while current_node.right is not None:
            current_node = current_node.right

        return current_node

    #================================================================================================
    
    def find_split_node(self, x1, x2) -> RangeTreeNode:

        split_node = self.root

        while split_node.left is not None: #When both paths are common and we reach a leaf
            if (x1 <= split_node.value) and (x2 <= split_node.value):
                split_node = split_node.left

            elif (x1 > split_node.value) and (x2 > split_node.value):
                split_node = split_node.right

            else:
                break

        return split_node
    
    #================================================================================================
    
    def report_leaves(self, node = None) -> "list[RangeTreeNode]":
        if node == None:
            node = self.root

        result = []

        if node.left is not None:
            result = result + self.report_leaves(node.left)
        else:
            return [node]

        if node.right is not None:
            result = result + self.report_leaves(node.right)

        return result
    
    #================================================================================================

    def range_search(self, x1, x2) -> "list[RangeTreeNode]":
        '''
            A method for executing inclusive range queries

            Parameters:
            - x1: Lower bound
            - x2: Upper bound

            Setting any of the parameters as None will make the query one-sided

            Setting both parameters as None functions as a "Don't Care" (return everything)

            Returns: A list of RangeTreeNodes (the subtrees whose leaves contain the answer).
            The subtrees are guaranteed to return the answer in ascending order
        '''

        
        #Preprocessing
        if x1 is None:
            x1 = self.find_smallest().value
        
        if x2 is None:
            x2 = self.find_biggest().value

        if type(x1) is str:
            x1 = x1.lower()

        if type(x2) is str:
            x2 = x2.lower()

        result = []

        split_node = self.find_split_node(x1, x2)

        p1 = []
        p2 = []

        s1 = None
        s2 = None

        if split_node.left is None: #split_node is a leaf, because the search paths are common
            s1 = split_node
            s2 = split_node
        else:
            s1, p1 = self.search(x1, split_node.left, "right")
            s2, p2 = self.search(x2, split_node.right, "left")
                    
        #Report nodes
        #===================================================================
        
        if s1.value >= x1 and s1.value <= x2:
            result.append(s1)

        result = result + p1 + p2

        '''
        for x in p1:
            result = result + self.report_leaves(x)

        for x in p2:
            result = result + self.report_leaves(x)
        '''

        if s1 != s2 and s2.value <= x2 and s2.value >= x1:
            result.append(s2)

        return result
    
    #================================================================================================

    def left_rotation(self, node):
        '''
        Performs a left rotation on the node passed as a parameter

        Returns: The node that took its place in the tree after the rotation (the original right child)
        '''

        child = node.right
        parent = node.parent

        #Step 1: The parent needs to have the child node as its new child
        if parent is not None:
            if node == parent.left:
                parent.left = child
            elif node == parent.right:
                parent.right = child

            child.parent = parent

        else: #node is the root
            child.parent = None
            self.root = child

        #Step 2: Original node needs to get child node's left subtree as its new right subtree
        node.right = child.left
        child.left.parent = node

        #Step 3: Child becomes the parent
        child.left = node
        node.parent = child

        #Update heights and hb starting from the lowest node (node, then child)
        node.height = max(node.left.height, node.right.height) + 1
        node.hb = node.right.height - node.left.height

        child.height = max(child.left.height, child.right.height) + 1
        child.hb = child.right.height - child.left.height

        return child
    
    #================================================================================================

    def right_rotation(self, node):
        '''
        Performs a right rotation on the node passed as a parameter

        Returns: The node that took its place in the tree after the rotation (the original left child)
        '''

        child = node.left
        parent = node.parent

        #Step 1: The parent needs to have the child node as its new child
        if parent is not None:
            if node == parent.left:
                parent.left = child
            elif node == parent.right:
                parent.right = child

            child.parent = parent

        else: #node is the root
            child.parent = None
            self.root = child

        #Step 2: Original node needs to get child node's right subtree as its new left subtree
        node.left = child.right
        child.right.parent = node

        #Step 3: Child becomes the parent
        child.right = node
        node.parent = child

        #Update heights and hb starting from the lowest node (node, then child)
        node.height = max(node.left.height, node.right.height) + 1
        node.hb = node.right.height - node.left.height

        child.height = max(child.left.height, child.right.height) + 1
        child.hb = child.right.height - child.left.height

        return child
    
    #================================================================================================

    def left_right_rotation(self, node):
        '''
        Performs a left-right rotation on the node passed as a parameter

        Returns: The node that took its place in the tree after the rotation
        '''

        self.right_rotation(node.right)
        return self.left_rotation(node)
    
    #================================================================================================

    def right_left_rotation(self, node):
        '''
        Performs a right-left rotation on the node passed as a parameter

        Returns: The node that took its place in the tree after the rotation
        '''

        self.left_rotation(node.left)
        return self.right_rotation(node)
    
    #================================================================================================
    
    def balance(self, node):
        '''
        Starts moving upwards in the tree, updating heights and balances. Performs rotation where necessary

        node is a leaf's parent. It's the node where the search ended during an insertion
        '''

        node.height = 1

        current_node = node.parent
        previous_node = node

        while current_node is not None:

            current_node.height = max(current_node.left.height, current_node.right.height) + 1
            current_node.hb = current_node.right.height - current_node.left.height

            if current_node.hb == 0:
                break

            elif current_node.hb == 2:

                if previous_node.hb == 1:
                    self.left_rotation(current_node)

                elif previous_node.hb == -1:
                    self.left_right_rotation(current_node)

                break

            elif current_node.hb == -2:

                if previous_node.hb == -1:
                    self.right_rotation(current_node)

                elif previous_node.hb == 1:
                    self.right_left_rotation(current_node)

                break

            previous_node = current_node
            current_node = current_node.parent

            
    #================================================================================================

    def insert(self, x: DataPoint) -> None:

        value = x[index[self.dimension]]

        #For names, use lastname for indexing
        if type(value) is str:
            value = value.split()[-1].lower()

        if self.root == None:
            self.root = RangeTreeNode(value, [x])
        else:
            leaf = self.search(value)
            
            if value == leaf.value:
                leaf.data.append(x)
            elif value < leaf.value:
                leaf.left = RangeTreeNode(value, [x], leaf)
                leaf.right = RangeTreeNode(leaf.value, leaf.data, leaf)

                leaf.value = value
                leaf.data = None

                #self.balance(leaf)
            else:
                leaf.left = RangeTreeNode(leaf.value, leaf.data, leaf)
                leaf.right = RangeTreeNode(value, [x], leaf)

                leaf.data = None

                #self.balance(leaf)

    #================================================================================================

    def query_driver(self, q1, q2, q3) -> "list[DataPoint]":
        '''
            An interface for executing queries. Accepts 3 parameters, one for each dimension.

            Accepted types:
            - int/ str for exact match
            - list for range query
                - [int/str, int/str] for two-sided range query
                - Putting None in any side will make the query one-sided
                - [None, None] is equivalent to just None
            - None means "ignore this dimension"

            Returns:
            A list of DataPoints that belong in the answer
        '''
        q = None

        if self.dimension == 3:
            q = q1
        elif self.dimension == 2:
            q = q2
        elif self.dimension == 1:
            q = q3

        local_res: list[RangeTreeNode] = None
        res = []

        if type(q) is int or type(q) is str: #Exact match search
            local_res = [self.search(q)]
            if local_res[0].value != q:
                return None
        elif type(q) is list: #Range search
            local_res = self.range_search(q[0], q[1])
            if len(local_res) == 0:
                return None
        elif q is None: #Don't care for this dimension
            if self.dimension > 1:
                #print(self.dimension, "DONT CARE")
                return self.root.alt_tree.query_driver(q1, q2, q3)
            else:
                return [dp.id for leaf in self.report_leaves() for dp in leaf.data]

        for node in local_res:
            if self.dimension > 1:
                next_dim_res = node.alt_tree.query_driver(q1, q2, q3)
                if next_dim_res is not None:
                    res = res + next_dim_res
            else:
                res = res + [dp.id for leaf in self.report_leaves(node) for dp in leaf.data]

        return res
        
    #================================================================================================

    def traverse_inorder(self, node):
        if node == None:
            return

        self.traverse_inorder(node.left)
        print(node.value)
        self.traverse_inorder(node.right)

    #================================================================================================

    def traverse_preorder(self, node = None):
        if node == None:
            node = self.root

        print(f" {None if node.left is None else node.left.value} <-- {node.value} --> {None if node.right is None else node.right.value}")

        if node.left is not None:
            self.traverse_preorder(node.left)

        if node.right is not None:
            self.traverse_preorder(node.right) 

#================================================================================================

if __name__ == "__main__":
    
    data = None
    with open("./data/out2.json", "r", encoding = "utf-8") as f:
        data = json.load(f)

    tree = RangeTree(data)

    result = tree.query_driver(["A", "C"], [0,3], [0,1])
    #result = tree.query_driver(None, None, None)

    print(len(result))
 
    if result is not None:
        for dp in result:
            print(dp.id)
