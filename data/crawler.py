import requests
from bs4 import BeautifulSoup, NavigableString
import string
import re
import json

def parse_dblp(url, parse_awards:bool):
    #Based on https://dblp.org/faq/How+can+I+fetch+all+publications+of+one+specific+author.html

    if re.search(".html$", url):
        url = url.replace("html", "xml")
    elif re.search("^https://dblp.org/pid/", url):
        url = url + ".xml"
    else:
        #Sometimes DBLP urls have a bad format that cannot give us the xml file
        #In this case, redirection happens to the actual page
        #...so we get the redirection link, and from that, the link to the xml file
        url = requests.head(url, allow_redirects=True).url.replace("html", "xml")

    res = requests.get(url)
    soup = BeautifulSoup(res.text, features="xml")
    dblp_records = soup.find("dblpperson")["n"]

    dblp_awards = 0

    if parse_awards:
        dblp_awards = len(soup.find_all("note", attrs={"type": "award"}))

    return (dblp_records, dblp_awards)

#===================================================================================================================================
#===================================================================================================================================

def parse_page(a_tag):
    print("Parsing page of", a_tag.text.encode().decode())

    res = requests.get("https://en.wikipedia.org" + a_tag["href"])
    soup = BeautifulSoup(res.text, "html.parser")

    data = {}

    #Award count
    #===================================================================================================================================
    award_count = 0

    #If someone has awards, they will be either in the infobox to the side of the page, or in an "Awards" header
    #If awards are listed in the infobox, they are ALWAYS (sometimes) correct
    #If they are ONLY mentioned in a dedicated section, they are usually in the form of a list (<ul>)
    #If they are mentioned in both, it's possible awards are listed alongside other honors, so we may count too many awards. In this case we need to check the infobox.
    #	See: https://en.wikipedia.org/wiki/Rediet_Abebe
    #So the infobox should always take priority, and if it doesn't exist, check section

    #Sometimes, awards in the dedicated section are NOT in a list (not very common)
    #Not much can be done here
    #	See: https://en.wikipedia.org/wiki/George_Boole
    #Other people have awards, but we don't see that information in an organized way at all
    #	See: https://en.wikipedia.org/wiki/Sanjeev_Arora

    award_infobox = soup.find(class_ = "infobox-label", string = re.compile(".*[Aa]ward.*"))

    if award_infobox:
        awards_data = award_infobox.find_next("td", class_ = "infobox-data")

        #It is possible that there is an awards section in the infobox, but no awards list exist
        #This can happen in the awards are not in a list, or if the person only has one award
        #If no list exists, the awards are separated with <br> tags, so we count those
        #	See: https://en.wikipedia.org/wiki/Manindra_Agrawal or https://en.wikipedia.org/wiki/David_P._Anderson

        awards_ul = awards_data.find("ul", class_ = None)

        if awards_ul:
            award_count = len(awards_ul.find_all("li"))
        else:
            award_count = len(awards_data.find_all("br")) + 1
    else:
        awards_section = soup.find("span", id=re.compile(".*[Aa]wards.*"))
        if awards_section:
            #Find the list between this and the next header
            #This is necessary, because sometimes the awards are not in a list, and if we searched for the next list, we would return an unrelated list
            awards_section = awards_section.parent
            next = awards_section.next_sibling
            pattern = re.compile("^h\d") #Check if the next element is a header
            
            while isinstance(next, NavigableString) or not pattern.search(next.name):
                if next.name == "ul":
                    break
                next = next.next_sibling

            if pattern.search(next.name):
                #There is no list in awards section. Don't know what to do here (there's 69 of these cases)
                #An idea could be to use the number of awards listed in the DBLP page, assuming the person has one
                #-1 means that this person has an awards section and we may be able to find their awards in the dblp page (see DBLP)
                award_count = -1
            else:
                award_count = len(next.find_all("li"))

    #DBLP
    #===================================================================================================================================
    dblp_tag = None
    references = soup.find("span", id = "References")

    if references:
        dblp_tag = references.find_next("a", href = re.compile("^https://dblp.org/pid/"))
        if not dblp_tag:
            dblp_tag = references.find_next("a", href = re.compile("https.*dblp\..*"))

    dblp_records = 0
    dblp_awards = 0

    if dblp_tag:
        (dblp_records, dblp_awards) = parse_dblp(dblp_tag["href"], award_count == -1)
        if award_count == -1:
            award_count = dblp_awards
    elif award_count == -1:
        award_count = 0

    #Education
    #===================================================================================================================================

    span_tag = soup.find('span', id= re.compile(".*[Ee]ducation.*"))

    p_tag = None

    if span_tag:
        p_tag = span_tag.find_next(['ul', 'p']).get_text()

    #===================================================================================================================================

    data["name"] = a_tag.text.encode().decode()
    data["awards"] = award_count
    data["dblp_records"] = int(dblp_records)

    if p_tag:
        data["education"] = p_tag.encode().decode()

    data["wikipedia_link"] = 'https://en.wikipedia.org' + a_tag['href']

    if dblp_tag:
        data["dblp_link"] = dblp_tag["href"]

    return data

#===================================================================================================================================
#===================================================================================================================================

if __name__ == "__main__":
    res = requests.get("https://en.wikipedia.org/wiki/List_of_computer_scientists")
    soup = BeautifulSoup(res.text, "html.parser")

    output = []

    alphabet_list = list(string.ascii_uppercase)

    for letter in alphabet_list:
        letter_header = soup.select_one("h2 > span.mw-headline#" + letter) #Not actually the header, but the <span> inside the header. The header is the parent

        if letter_header:
            namelist = letter_header.parent.find_next_sibling()
            linklist = namelist.select("li > a:first-child")

            for x in linklist:
                output.append(parse_page(x))
                
    with open("out.json", "w", encoding="utf-8", ) as f:
        f.write(json.dumps(output, indent = "\t", ensure_ascii=False))