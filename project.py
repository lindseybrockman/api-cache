import json
import psycopg2

from flask import Flask, redirect, render_template, request, url_for
from flask.ext.sqlalchemy import get_debug_queries, SQLAlchemy
from redis import Redis
from sqlalchemy.sql import text

from models import Recipe

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

DB_CONNECTION_PARAMS = "dbname=recipe user=lindseybrockman"

@app.route('/')
def index():
    """
    Index Page
    """
    return 'Hello World!'


@app.route('/recipe/', defaults={'recipe_id': None})
@app.route('/recipe/<int:recipe_id>/')
def recipe(recipe_id):
    """
    GET recipes
    """
    if recipe_id:
        # show single recipe
        recipes = [Recipe.query.get_or_404(recipe_id)]
    else:
        # show all recipes
        recipes = Recipe.query.order_by(Recipe.rating.desc()).all()[:100]
    print get_debug_queries()
    return render_template('recipe.html', recipe_id=recipe_id, recipes=recipes)


@app.route('/recipe/add/', methods=['GET', 'POST'])
def add_recipe():
    """
    View for adding new recipes
    """
    if request.method == 'POST':
        name = request.form.get('name')
        cook_time = request.form.get('cook_time')
        prep_time = request.form.get('prep_time')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')
        rating = request.form.get('rating')

         # add the new recipe to the db
        connection = psycopg2.connect(DB_CONNECTION_PARAMS)
        cursor = connection.cursor()
        cursor.execute(
            """
                INSERT INTO recipe (name, cook_time, prep_time, ingredients, instructions, rating)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (name, cook_time, prep_time, ingredients, instructions, rating)
        )
        connection.commit()
        new_recipe_id = cursor.fetchone()[0]
        # flush stale keys
        # flush_stale(name)
        # flush_stale(ingredients)
        # finally, redirect to the new recipe
        return redirect('/recipe/{}/'.format(new_recipe_id))
    return render_template('recipe_add.html')


@app.route('/search/recipe/', defaults={'search_term': ''}, methods=['GET', 'POST'])
@app.route('/search/recipe/<search_term>', methods=['GET'])
def search(search_term):
    return base_search(search_term)

@app.route('/search-cache/recipe/', defaults={'search_term': ''}, methods=['GET', 'POST'])
@app.route('/search-cache/recipe/<search_term>', methods=['GET'])
def search_cached(search_term):
    return base_search(search_term, cache=True)


def base_search(search_term, cache=False):
    """
    Search API
    """
    if request.method == 'POST':
        search_term = request.form['query']

    query = """
        SELECT
            name,
            id,
            ingredients,
            instructions,
            prep_time,
            cook_time,
            rating
        FROM
            recipe
        WHERE
            name like %s
            OR ingredients like %s
        ORDER BY
            rating DESC,
            name
    """

    # If we're using the cached search, try to get result from cache
    redis = Redis()
    result = None
    if cache:
        result = redis.get('cache:{}'.format(search_term))

    # If the cache doesn't contain the key, or 
    # if we aren't using caching, fall back on the DB
    if not result:
        connection = psycopg2.connect(DB_CONNECTION_PARAMS)
        cursor = connection.cursor()

        # following query paramter is not left or right anchored
        # so %Chicken% will match 'Chicken Soup', 'Fried Chicken', and 'BBQ Chicken Wings'
        like_search = '%{}%'.format(search_term)

        # print query for debugging
        print cursor.mogrify(query, (like_search, like_search, ))
        cursor.execute(query, (like_search, like_search, ))

        # get the results
        rows = cursor.fetchall()
        columns = cursor.description
        result = [dict(zip([col[0] for col in columns], row)) for row in rows]
        result = json.dumps(result)
        # If we're using a caching view
        # add the new key to the cache
        if cache:
            redis.set('cache:{}'.format(search_term), result)

    if request.method == 'POST':
        return render_template('recipe.html', search_term=search_term, recipes=json.loads(result))

    return result


def flush_stale(text):
    keys = set()
    for m in range(len(text)):
        for n in range(m):
            keys.add(text[n:m])
    if '' in keys:
        keys.remove('')
    keys = list(keys)
    redis = Redis()
    for key in keys:
        redis.delete('cache:{}'.format(key))


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


if __name__ == '__main__':
    app.run(debug=True)

