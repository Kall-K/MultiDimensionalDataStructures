#im looking for 
#tags with:
#1)Education
#2)Early_life_and_education
#3)Education_and_early_life
from bs4 import BeautifulSoup
import requests

counter = 0
local_path = 'C:/Users/kalli/Desktop/education_url.'

f = open("C:/Users/kalli/Desktop/scientist_url.txt", "r", encoding='UTF8')
f_ = open(local_path+'txt', "a", encoding='UTF8')

for url in f:
    url = url[:-1]
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    list(soup.children)
    
    span_tag = soup.find('span', id=['Education', 'Early_life_and_education', 'Education_and_early_life'])
    
    if span_tag:
        p_tag = span_tag.find_next(['ul', 'p']).get_text()
        #print(p_tag if p_tag else "No matching <p> tag found.")
        #f = open(local_path+'txt', "a", encoding='UTF8')
        f_.write(p_tag+'\n')
        #f.close()
        
    else:
        #print("No matching <span> tag found.")
        #f = open(local_path+'txt', "a", encoding='UTF8')
        f_.write("No education info found.\n\n")
        #f.close()
        counter +=1
        
    #break
print(counter)
f.close()
f_.close()



  











