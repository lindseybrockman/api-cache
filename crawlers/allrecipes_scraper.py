import requests
from bs4 import BeautifulSoup

#json will looks something like:
#{'name': 'name', 'prep_time': 'prep_time', 'cook_time': 'cook_time', 'ingredients': 'ingredients', 'instructions': 'instructions'}

class Scraper(object):

    def __init__(self): 
        self.category_links = set()
        self._finished = False
        self.recipe_links = set()
        self.dead_ends = set()
        self.recipe_data = []
        self.failed_because_redirect = 0

    def scrape(self, response):
        while not self._finished:
            if len(self.category_links) != 0:
                response = self._get_next_link()
            if response:
                soup = BeautifulSoup(response.content)
                print "CURRENTLY AT: {}".format(response.url)
                print "visted {}".format(len(self.dead_ends))
                print "recipes found {}".format(len(self.recipe_links))
                print "failed GETS: {}".format(self.failed_because_redirect)
                for link in soup.find_all("a"):
                    href = link.get("href")
                    if href:
                        if href.startswith("/"):
                            href = "http://allrecipes.com" + href
                        if len(href.split("?")) == 1 or "Page" not in href.split("?")[1]:
                            href = href.split("?")[0]
                        if '/recipes/' in href and href not in self.dead_ends:
                            self.category_links.add(href)
                        if '/Recipe/' in href:
                            self.recipe_links.add(href)

                self.dead_ends.add(response.url)
            else:
                self._finished = True
        print "Scraped {} category links".format(len(self.category_links))
        print "Scraped {} unique recipes".format(len(self.recipe_links))

    def _get_next_link(self):
        for link in self.category_links:
            if link not in self.dead_ends:
                try:
                    res = requests.get(link)
                    if res.url not in self.dead_ends and res.status_code not in [404, 500]:
                        return res
                    else:
                        self.dead_ends.add(link)
                        self.failed_because_redirect += 1
                except:
                    self.dead_ends.add(link)
        return None

    def build_recipes(self, recipe_links):
        for link in recipe_links:
            resp = requests.get(link)
            soup = BeautifulSoup(resp.content)
            name = soup.find("h1", {"id": "itemTitle"})
            prep_time = soup.find("span", {"id": "prepMinsSpan"})
            cook_time = soup.find("span", {"id": "cookMinsSpan"})
            ingredients = soup.find("ul", class_="ingredient-wrap")
            instructions = soup.find("div", {"itemprop": "recipeInstruction"})
            recipe_data = {
                "name": name,
                "prep_time": prep_time,
                "cook_time": cook_time,
                "ingredients": ingredients,
                "instructions": instructions,
            }
            self.recipe_data.append(recipe_data)

if __name__ == '__main__':
    resp = requests.get('http://allrecipes.com/') 
    scraper = Scraper()
    scraper.scrape(resp)
    scraper.build_recipes(scraper.recipe_links)

