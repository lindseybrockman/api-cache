import json


class Recipe(object):
	'''
	An Epicurious recipe.
	'''
	def __init__(self, servings, description, ingredients, preparation):
		self.servings = servings
		self.description = description
		self.ingredients = ingredients
		self.preparation = preparation

	def to_json(self):
		recipe = {
			'servings': self.servings,
			'description': self.description,
			'ingredients': self.ingredients,
			'preparation': self.preparation}

		return json.dumps(recipe)


class Ingredient(object):
	'''
	A single ingredient.
	'''
	def __init__(self, name, measurement, unit):
		self.name = name
		self.measurement = measurement
		self.unit = unit


class CompositeIngredient(Ingredient):
	'''
	An ingredient composed of ingredients.
	'''
	ingredients = []

	def add(self, ingredient):
		self.ingredients.append(ingredient)
