import requests
from bs4 import BeautifulSoup

resp = requests.get('http://allrecipes.com/recipes/appetizers-and-snacks/')
soup = BeautifulSoup(resp.content)

links = set()
for link in soup.find_all("a", class_="img-link"):
    links.add(link.get("href"))
#soup.find("div", class_="page_navigation_nav").children
# return links
print len(links)
