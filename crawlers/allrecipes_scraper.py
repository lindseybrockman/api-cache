import csv
import json
import thread
import requests
from bs4 import BeautifulSoup

class Scraper(object):
    """
    A Scraper object will take in a response object
    and start recursively crawling that site for
    recipe data
    """

    def __init__(self):
        self._finished = False
        self.category_links = set()
        self.recipe_links = set()
        self.dead_ends = set()
        self.recipe_data = []

    def scrape(self, response, stop_size=8000):
        while not self._finished:
            # if we've crawled this site before,
            # go to the next link
            if len(self.category_links) != 0:
                response = self._get_next_link()
            # if get_next_link returns a new link and
            # we haven't grabbed more than 20K recipes,
            # keep scraping
            if response and len(self.recipe_links) <= stop_size:
                soup = BeautifulSoup(response.content)
                print "visted {}".format(len(self.dead_ends))
                print "recipes found {}".format(len(self.recipe_links))
                for link in soup.find_all("a"):
                    href = link.get("href")
                    if href:
                        if href.startswith("/"):
                            href = "http://allrecipes.com" + href
                        # remove get params, unless we are paginating.
                        if len(href.split("?")) == 1 or "Page" not in href.split("?")[1]:
                            href = href.split("?")[0]
                        # /recipes/ links are categories or articles
                        if '/recipes/' in href and href not in self.dead_ends:
                            self.category_links.add(href)
                        # /Recipe/ links are actual recipes
                        if '/Recipe/' in href:
                            self.recipe_links.add(href)
                # don't visit the same thing more than once
                self.dead_ends.add(response.url)
            else:
                self._finished = True
        print "Scraped {} category links".format(len(self.category_links))
        print "Scraped {} unique recipes".format(len(self.recipe_links))

    def _get_next_link(self):
        """
        Return the next unvisited link
        """
        for link in self.category_links:
            if link not in self.dead_ends:
                try:
                    res = requests.get(link)
                    if res.url not in self.dead_ends and res.status_code not in [404, 500]:
                        self.dead_ends.add(link) 
                        return res
                except:
                    self.dead_ends.add(link)
        return None

    def build_recipes(self, chunk_size=2000):
        recipe_list = list(self.recipe_links)
        range_size = len(recipe_list)/chunk_size
        if len(recipe_list) < chunk_size:
            self._build_recipes(recipe_list)
        else:
            for i in xrange(range_size):
                thread.start_new_thread(self._build_recipes, (recipe_list[i*chunk_size: (i+1)*chunk_size-1], ))

    def _build_recipes(self, recipe_links):
        """
        parse recipe data
        """
        for link in recipe_links:
            resp = requests.get(link)
            soup = BeautifulSoup(resp.content)
            name = soup.find("h1", {"id": "itemTitle"})
            prep_time = soup.find("span", {"id": "prepMinsSpan"})
            cook_time = soup.find("span", {"id": "cookMinsSpan"})
            ingredients = soup.find("ul", class_="ingredient-wrap")
            instructions = soup.find("div", class_="directions")
            if name:
                recipe_data = {
                    "name": name.text,
                    "prep_time": prep_time.text if prep_time else '',
                    "cook_time": cook_time.text if cook_time else '',
                    "ingredients": ingredients.text if ingredients else '',
                    "instructions": instructions.text if instructions else '',
                }
                self.recipe_data.append(recipe_data)
        print "PARSED: {}".format(len(self.recipe_data))

    def save_as_json(self):
        with open('all_recipes.json', 'w') as outfile:
            json.dump(self.recipe_data, outfile)

    def save_as_csv(self):
        with open('all_recipes.csv', 'w')  as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([
                'name',
                'prep_time',
                'cook_time',
                'ingredients',
                'instructions'
            ])
            for row in self.recipe_data:
                name = row['name'].replace(',', ';').replace('"', '').encode('utf-8')
                prep_time = row['prep_time'].replace(',', ';').replace('"', '').encode('utf-8')
                cook_time = row['cook_time'].replace(',', ';').replace('"', '').encode('utf-8')
                ingredients = row['ingredients'].replace(',', ';').replace('"', '').encode('utf-8') 
                instructions = row['instructions'].replace(',', ';').replace('"', '').encode('utf-8') 
                csv_writer.writerow([
                    name,
                    prep_time,
                    cook_time,
                    ingredients,
                    instructions
                ])

if __name__ == '__main__':
    resp = requests.get('http://allrecipes.com/')  
    scraper = Scraper()
    scraper.scrape(resp, 2000)
    scraper.build_recipes()
    scraper.save_as_csv()

