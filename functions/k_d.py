from typing import Any
import json

split_order = {0: "name", 1: "dblp", 2: "awards"}

#================================================================================================

class DataPoint:

    def __init__(self, name: str, awards: int, dblp: int, education: str, id: int):
        self.data = {"name": name, "awards": awards, "dblp": dblp, "education": education, "id": id}

    def __getattr__(self, name: str) -> Any:

        if name == "lastname":
            return self.data["name"].split()[-1]
        
        val = self.data.get(name, None)

        if val is None:
            raise AttributeError
        
        return self.data[name]
    
    def __str__(self):
        return f"Name: {self.name}\nAwards: {self.awards}\nDBLP: {self.dblp}\n"
    
    def __getitem__(self, key: str):
        if key == "name":
            return self.data[key].split()[-1].lower()
        else:
            return self.data[key]
    
    def equal(self, other: "DataPoint"):
        '''
        Checks if two DataPoints are equal, not strictly, but in terms of indexing.
        This means that, while it does compare the points element-wise, it only uses lastname for the name comparison,
        since that's what we use for indexing.
        It also doesn't check education, as it's not part of the indexing
        '''
        return (self.lastname == other.lastname) and (self.awards == other.awards) and (self.dblp == other.dblp)
    
    def value(self, depth: int):
        '''
        Returns the value we use for the split.
        What this value actually represents (name, awards or dblp, in other words the discriminator)
        is determined from the current search depth, passed as a parameter.
        We assume that the splitting point always belongs in the dataset, and is in position len//2 (median or upper median) of a sorted index
        '''
        global split_order

        val = self.data[split_order[depth % 3]]

        if type(val) is str: 
            return val.split()[-1].lower() #Lastname
        else:
            return val
    
#================================================================================================
    
class KDNode:
    def __init__(self, data: list[DataPoint], left: "KDNode" = None, right: "KDNode" = None):
        self.left = left
        self.right = right

        #Actual data stored in the node. We assume node-oriented tree
        #Note that during a search operation, we need to report separately/ explicitly if this set of nodes belongs in the answer
        #It is a list because there may be multiple points with ALL coordinates the same
        self.data = data 

    def __str__(self):
        return f"Address: {id(self)}\nValue: {self.data}"
    
    def value(self, depth: int):
        return self.data[0].value(depth)
    
#================================================================================================
    
class KDTree:
    def __init__(self, dataset):
        self.dataset = []

        id = 1
        for scientist in dataset:
            self.dataset.append(DataPoint(
                    scientist["name"],
                    scientist["awards"],
                    scientist["dblp_records"],
                    scientist.get("education", "EMPTY"),
                    id
                ))
            id = id + 1
        
        #Pre-sorting
        #After this, we never have to sort again
        #When we split based on one dimension, we just filter the three indexes based on the split value, and sorting order gets maintained!
        name_index = sorted(self.dataset, key = lambda x: x.lastname)
        awards_index = sorted(self.dataset, key = lambda x: x.awards)
        dblp_index = sorted(self.dataset, key = lambda x: x.dblp)

        #Construct the KD tree from the sorted indices
        self.root = self.construct(0, {"name": name_index, "dblp": dblp_index, "awards": awards_index})

    #================================================================================================
    def construct(self, depth: int, indexes: dict[str, list[DataPoint]]) -> KDNode:
        '''
            Constructs the KD Tree using the 3 sorted indices.
            Discriminator is determined by the current depth

            Parameters:
                - depth: The depth of the node that we're about to create. It determines how to split the dataset like this:

                    depth % 3 gives us the dimension we use for splitting, based on the "split_order" dictionary

                    For example, split_order = {0: "name", 1: "dblp", 2: "awards"}

                    0: Split on name

                    1: Split on dblp

                    2: Split on awards

                - indexes: A map with all three sorted indexes
        '''
        global split_order
            
        index = indexes[split_order[depth % 3]]

        if len(index) == 0: #During the split, all points went to the other side
            return None

        if len(index) == 1: #We reached a leaf
            return KDNode(index)

        #Calculate the median
        median = index[len(index) // 2] #For simplicitly. There is no need for more in a static, node-oriented tree
        
        #The datapoints with value <= medianValue, sorted by name, dblp and awards
        left_indexes = {"name": [], "dblp": [], "awards": []}

        #The datapoints with value > medianValue, sorted by name, dblp and awards
        right_indexes = {"name": [], "dblp": [], "awards": []}

        #Datapoints that have ALL dimensions same as the median point
        #These will go in the current node as its data
        this_list = []

        for dp in indexes["name"]:
            if dp.value(depth) < median.value(depth):
                left_indexes["name"].append(dp)
            elif dp.value(depth) > median.value(depth):
                right_indexes["name"].append(dp)

            #If indexing value is equal to the splitting value, there is a chance that ALL dimensions are equal
            else: 
                if dp.equal(median): #Only add to this_list ONCE, doesn't matter where
                    this_list.append(dp)
                else:
                    left_indexes["name"].append(dp)

        for dp in indexes["dblp"]:
            if dp.value(depth) < median.value(depth):
                left_indexes["dblp"].append(dp)
            elif dp.value(depth) > median.value(depth):
                right_indexes["dblp"].append(dp)
            elif not dp.equal(median):
                left_indexes["dblp"].append(dp)

        for dp in indexes["awards"]:
            if dp.value(depth) < median.value(depth):
                left_indexes["awards"].append(dp)
            elif dp.value(depth) > median.value(depth):
                right_indexes["awards"].append(dp)
            elif not dp.equal(median):
                left_indexes["awards"].append(dp)

        '''
        with open(f"left_indexes_{depth}", "w") as f:
            json.dump(left_indexes, f, default = lambda dp: dp.data, indent=4)

        with open(f"right_indexes_{depth}", "w") as f:
            json.dump(right_indexes, f, default = lambda dp: dp.data, indent=4)
        '''

        left_child = self.construct(depth + 1, left_indexes)
        right_child = self.construct(depth + 1, right_indexes)
        return KDNode(this_list, left_child, right_child)
    
    def printKDTree(self, kdNode):
        for i in range(len(kdNode.data)):
            print(kdNode.data[i].id)
        if kdNode.left != None:
            self.printKDTree(kdNode.left)
        if kdNode.right != None:
            self.printKDTree(kdNode.right)
    
    def rangeQuery(self, kdNode, depth, up_bound, low_bound, result):
        global split_order
        upper = up_bound[split_order[depth % 3]]
        lower = low_bound[split_order[depth % 3]]

        check_R = check_L = False

        if (type(upper) is str):
            upper = upper.lower()
        if (type(lower) is str):
            lower = lower.lower()
        
        if kdNode.value(depth) >= lower: check_L = True
        else: check_R = True
        
        if kdNode.value(depth) >= upper: check_L = True
        else: check_R = True

        check = [False]*3
        for i in range(3):
            check[i]= self.inRange(kdNode.data[0], up_bound, low_bound, split_order[i])
        
        if all(check): 
            for i in range(len(kdNode.data)):
                result.append(kdNode.data[i].id)
        
        if check_L and kdNode.left != None:
            self.rangeQuery(kdNode.left, depth+1, up_bound, low_bound, result)
        if check_R and kdNode.right != None:
            self.rangeQuery(kdNode.right, depth+1, up_bound, low_bound, result)

        return result

    def inRange(self, node, up_bound, low_bound, key):
        return (node.__getitem__(key)<=up_bound[key]) and (node.__getitem__(key)>=low_bound[key])
        
#================================================================================================
def init_kdTree(data):
    return KDTree(data)

#================================================================================================

if __name__ == "__main__":
    #Initialize the dataset from the json file
    with open("./data/out2.json", "r", encoding = "utf-8") as f:
        data = json.load(f)
        
    tree = KDTree(data)
    # tree.printKDTree(tree.root)
    
    lower = {"name": "e", "dblp": 0, "awards": 0}#input
    upper = {"name": "x", "dblp": 10000, "awards": 1000}#input
    result = []
    result = tree.rangeQuery(tree.root, 0, upper, lower, result)        
     
    for r in result:
        print(r.__str__())                                         
    print(len(result)) 
