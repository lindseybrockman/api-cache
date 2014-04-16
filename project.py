from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    """
    Index Page
    """
    return 'Hello World!'


@app.route('/recipe', defaults={'recipe_id': None})
@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    """
    GET recipes
    """
    if recipe_id:
        # show single recipe
        pass
    else:
        # show all recipes
        pass


@app.route('/autocomplete/recipe', defaults={'search_term': None})
@app.route('/autocomplete/recipe/<search_term>')
def autocomplete(search_term):
    """
    Autocomplete API
    """
    if not search_term:
        # return all items
        pass
    else:
        query = """
            SELECT distinct(recipe_id) recipe_id, json_data
            FROM recipe_autocomplete
            WHERE token like '%{}%'
            """
"""
EXAMPLE DB ROW:
id    token    recipe_id    json_data: {name, url/id}
"""

if __name__ == '__main__':
    app.run(debug=True)
