import json
from typing import Any

index = {3: "dblp", 2: "name", 1: "awards"}

#d = {3: "name", 2: "dblp", 1: "awards"}

class DataPoint:

    def __init__(self, name: str, awards: int, dblp: int, education: str):
        self.data = {"name": name, "awards": awards, "dblp": dblp, "education": education}

    def __getattr__(self, name: str) -> Any:
        val = self.data.get(name, None)

        if val is None:
            raise AttributeError
        
        return self.data[name]
    
    def __str__(self):
        return f"Name: {self.name}\nAwards: {self.awards}\nDBLP: {self.dblp}\n"
    
    def __getitem__(self, key: str):
        return self.data[key]

class RangeTreeNode:

    def __init__(self, value: int, data: list[DataPoint], left: "RangeTreeNode" = None, right: "RangeTreeNode" = None):
        self.left = left
        self.right = right

        self.data = data
        self.value = value

        self.alt_tree: RangeTree = None

    def __str__(self):
        return f"{self.data}"
    
class RangeTree:
    '''
    dataset: Path to the json file containing the dataset
    '''

    def __init__(self, dataset: str | list[RangeTreeNode], dimension: int = 3):    
        self.dataset = dataset
        self.root = None
        self.dimension = dimension

        if self.dimension == 3: #Create tree from JSON file
            #Get the dataset as a JSON object
            data = None
            with open(self.dataset, "r", encoding = "utf-8") as f:
                data = json.load(f)

            for scientist in data:
                self.insert(
                DataPoint(
                    scientist["name"],
                    scientist["awards"],
                    scientist["dblp_records"],
                    scientist.get("education", "EMPTY")
                ))
        else: #Create tree using existing data in the dataset list
            for data_point in dataset:
                self.insert(data_point)

        if dimension > 1:
            self.create_alt_trees(self.root)

    def create_alt_trees(self, node: RangeTreeNode):
        
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


    def search(self, search_value: int,  start_node: RangeTreeNode = None, report: str = None) -> RangeTreeNode:
        '''
        Arguments:
            search_value: The value to search for

        Returns:
            node: The tree node where the search ended
        '''
        if start_node == None:
            start_node = self.root

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
    
    def report_leaves(self, node: RangeTreeNode = None) -> list[RangeTreeNode]:
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

    def range_search(self, x1, x2) -> list[RangeTreeNode]:

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


    def insert(self, x: DataPoint) -> None:

        value = x[index[self.dimension]]

        if self.root == None:
            self.root = RangeTreeNode(value, [x])
        else:
            leaf = self.search(value)
            
            if value == leaf.value:
                leaf.data.append(x)
            elif value < leaf.value:
                leaf.left = RangeTreeNode(value, [x])
                leaf.right = RangeTreeNode(leaf.value, leaf.data)

                leaf.value = value
                leaf.data = None
            else:
                leaf.left = RangeTreeNode(leaf.value, leaf.data)
                leaf.right = RangeTreeNode(value, [x])

                leaf.data = None

    def query_driver(self, q1: int | list[int] | None, q2: str | list[str] | None, q3: int | list[int] | None) -> list[RangeTreeNode]:

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
                return self.root.alt_tree.query_driver(q1, q2, q3)
            else:
                return self.report_leaves()

        for node in local_res:
            if self.dimension > 1:
                next_dim_res = node.alt_tree.query_driver(q1, q2, q3)
                if next_dim_res is not None:
                    res = res + next_dim_res
            else:
                res = res + self.report_leaves(node)

        return res
        

    def traverse_inorder(self, node: RangeTreeNode):
        if node == None:
            return

        self.traverse_inorder(node.left)
        print(node.value)
        self.traverse_inorder(node.right)

    def traverse_preorder(self, node: RangeTreeNode = None):
        if node == None:
            node = self.root

        print(f" {None if node.left is None else node.left.value} <-- {node.value} --> {None if node.right is None else node.right.value}")

        if node.left is not None:
            self.traverse_preorder(node.left)

        if node.right is not None:
            self.traverse_preorder(node.right) 

if __name__ == "__main__":
    tree = RangeTree("./data/out.json")

    result = tree.query_driver([100, 200], None, [5,10])

    for node in result:
        for dp in node.data:
            print(dp)