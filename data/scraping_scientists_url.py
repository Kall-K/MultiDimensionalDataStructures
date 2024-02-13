from bs4 import BeautifulSoup
import requests
import csv

a_tags= []
matching_urls = []
counter=0
#choose a path of ur preference to save txt & csv
local_path = 'C:/Users/kalli/Desktop/scientist_url.'

page = requests.get("https://en.wikipedia.org/wiki/List_of_computer_scientists")

soup = BeautifulSoup(page.content, 'html.parser')

list(soup.children)

full_list = soup.findAll('ul', class_=False)
 
for category in full_list:
    if(counter<24):
        counter+=1
        group_list = category.findAll('li')
        for weblink in group_list:
            url= weblink.find_all('a', href=True)[0].get_text()
            url = "https://en.wikipedia.org/wiki/" + url
            a_tags.append(url)

print('\n!\n',len(a_tags))

# export to csv file
with open(local_path+'csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(a_tags)
f.close()
# export to txt file
f = open(local_path+'txt', "w", encoding='UTF8')
for row in a_tags:
    f.write(row+'\n')
f.close()










