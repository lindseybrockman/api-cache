from time import sleep

import requests
from bs4 import BeautifulSoup

from models import (
	Recipe,
	Ingredient,
	CompositeIngredient)


class RecipeScraper(object):

	BASE_URL = 'http://www.epicurious.com'


class SectionScraper(RecipeScraper):

	URL = None	# define this in subclass
	DEAD_ENDS = []  # define a set of links to skip

	@property
	def url(self):
		return self.BASE_URL + self.URL

	@property
	def dead_ends(self):
		return [self.URL + x for x in self.DEAD_ENDS]

	def get_links(self, url, selector, paged=False):
		'''
		Gets links off of a page given the url and selector.
		'''
		response = requests.get(url)
		soup = BeautifulSoup(response.text)
		html_links = soup.select(selector)
		links = [
			self.BASE_URL + x.attrs['href'] for x in html_links
			if x.attrs['href'] not in self.dead_ends]
		return links

	def get_parent_links(self, selector, paged=False):
		'''
		Gets the links in the left nav, from a page like this:
		http://www.epicurious.com/articlesguides/
		'''
		return self.get_links(self.url, selector)

	def get_children_links(self, parent_links, selector, paged=False):
		'''
		Gets the links from the section in the middle, from a page like this:
		http://www.epicurious.com/articlesguides/bestof
		'''
		links = []
		for link in parent_links:
			if paged:
				page_links = self.harvest_paged_links(link, selector)
			else:
				page_links = self.get_links(link, selector)
			links += page_links
		return links

	def harvest_paged_links(self, start_page, selector):
		'''
		Takes the first page with recipes, figures out how many pages
		there are, and goes through each one gathering recipe links.
		'''
		links = self._harvest_paged_links(start_page, selector, [])
		return links

	def _harvest_paged_links(self, start_page, selector, links):
		'''
		Recursive helper for gathering paged links.
		'''
		# If we don't have a page, we're done.
		if not start_page:
			return links

		# Open up the page and get the links
		response = requests.get(start_page)
		soup = BeautifulSoup(response.text)
		html_links = soup.select(selector)

		# If it doesn't have links we want, we're done.
		if not html_links:
			return links

		# Gather the links and add them to our collection
		new_links = [self.BASE_URL + x.attrs['href'] for x in html_links]
		links += new_links

		# Find out if there is another page.
		prev_next = soup.select('div#bNext a')
		next_page = None
		for button in prev_next:
			if button.text == 'next':
				next_page = self.BASE_URL + button.attrs['href']

		print next_page
		return self._harvest_paged_links(next_page, selector, links)


	def scrape(self):
		'''
		Override in subclasses.
		'''
		return NotImplemented()


class RecipesMenuScraper(SectionScraper):

	URL = '/recipesmenus/'

	def scrape(self):
		# Get the main page's links
		page_links = self.get_parent_links('.nav_item a.primary_nav_item')
		return self.cycle(page_links, [])

	def cycle(self, links, recipe_links):
		if not links:
			return recipe_links

		# Test for recipe links
		new_recipe_links = self.get_children_links(links, 'div.recipe_result_right a.recipe_detail_lnk', paged=True)
		if new_recipe_links:
			recipe_links += new_recipe_links
			return recipe_links

		# Try for article links
		article_links = self.get_children_links(links, 'a.recipe_detail_lnk')

		return self.cycle(article_links, recipe_links)

if __name__ == '__main__':
	scraper = RecipesMenuScraper()
	print scraper.scrape()