import requests
from bs4 import BeautifulSoup

#json will looks something like:
#{'name': 'name', 'prep_time': 'prep_time', 'cook_time': 'cook_time', 'ingredients': 'ingredients', 'instructions': 'instructions'}

class Scraper(object):

    def __init__(self, response):
        self.response = response
        self.category_links = set()
        self.recipe_links = set()
        self.visited_links = set()
        self.recipe_data = []

    def scrape(self, response=None):
        if not response:
            response = self.response

        soup = BeautifulSoup(response.content)

        for link in soup.find_all("a"):
            if 'recipes' in link.get("href"):
                print "adding category link {}".format(link.get("href")) 
                category_links.add(link.get("href"))
            if 'Recipe' in link.get("href"):
                print "adding recipe link {}".format(link.get("href"))
                recipe_links.add(link.get("href")

        self.visited_links.add(response.url)

        for link in self.category_links:
            if link not in self.visited_links:
                self.scrape(requests.get(link))

        # and now we've gone through all the category links
        print "Scraped {} category links".format(len(self.category_links))
        print "Scraped {} unique recipes".format(len(self.recipe_links))
        self.build_recipes(self.recipe_links).format(len(self.recipe_links))

    def build_recipes(self, recipe_links):
        for link in recipe_links
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

#soup.find("div", class_="page_navigation_nav").children
# return links
print len(links)

if __name__ == '__main__':
    resp = requests.get('http://allrecipes.com/') 
    scraper = Scraper(resp)
    scraper.scrape()
