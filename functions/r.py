import matplotlib.pyplot as plt


class Box:
    def __init__(self,top,right,bottom,left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
    
    def getx(self):
        x = [self.left, self.right, self.right, self.left, self.left]
        return x
    
    def gety(self):
        y = [self.top, self.top, self.bottom, self.bottom, self.top]
        return y
    

test_list = [
	{
		"name": "Atta ur Rehman Khan",
		"awards": 10,
		"dblp_records": 0,
		"wikipedia_link": "https://en.wikipedia.org/wiki/Atta_ur_Rehman_Khan"
	},
	{
		"name": "Wil van der Aalst",
		"awards": 0,
		"dblp_records": 1104,
		"wikipedia_link": "https://en.wikipedia.org/wiki/Wil_van_der_Aalst",
		"dblp_link": "https://dblp.org/pid/a/WilMPvanderAalst"
	},
	{
		"name": "Scott Aaronson",
		"awards": 4,
		"dblp_records": 228,
		"wikipedia_link": "https://en.wikipedia.org/wiki/Scott_Aaronson",
		"dblp_link": "https://dblp.org/pid/56/1358"
	},
	{
		"name": "Rediet Abebe",
		"awards": 3,
		"dblp_records": 0,
		"wikipedia_link": "https://en.wikipedia.org/wiki/Rediet_Abebe"
	}
]

def vis_data(boxes):
    x = []
    y = []
    for i in test_list:
        x.append(i['awards'])
        y.append(i['dblp_records'])
    
    plt.scatter(x, y) 
    plt.xlabel('awards') 
    plt.ylabel('dblp records') 
    plt.title('Graph')
    for i in test_list:
        label = i['name']
        plt.annotate(label, (i["awards"], i["dblp_records"]),
                    textcoords="offset points", xytext=(0,10), ha='center')
    
    for b in boxes:
        plt.plot(b.getx(), b.gety())

    plt.show()




def make_tree(data):
    for i in test_list:
        pass



box1 = Box(100,10,6,2)
vis_data([box1])
