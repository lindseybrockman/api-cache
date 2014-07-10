import json
import psycopg

from flask import Flask, render_template, request
from flask.ext.sqlalchemy import get_debug_queries, SQLAlchemy
from redis import Redis
from sqlalchemy.sql import text

from models import Recipe

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

@app.route('/')
def index():
    """
    Index Page
    """
    return 'Hello World!'


@app.route('/recipe/', defaults={'recipe_id': None})
@app.route('/recipe/<int:recipe_id>')
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


@app.route('/search/recipe/', defaults={'search_term': ''}, methods=['GET', 'POST'])
@app.route('/search/recipe/<search_term>', methods=['GET'])
def search(search_term):
    return _search(search_term)

@app.route('/search-cache/recipe/', defaults={'search_term': ''}, methods=['GET', 'POST'])
@app.route('/search-cache/recipe/<search_term>', methods=['GET'])
def search_cached(search_term):
    return _search(search_term, cache=True)


def _search(search_term, cache=False):
    """
    Search API
    """
    if request.method == 'POST':
        search_term = request.form['query']

    query = build_query(search_term)

    # Try to get result from cache
    redis = Redis()
    result = redis.get(search_term)

    # If the cache doesn't contain the key, fall back on the DB
    if not result:
        cursor = db.engine.execute(text(query), search_term=formatted_search_term)
        rows = cursor.fetchall()
        columns = cursor.keys()
        result = [dict(zip(columns, row)) for row in rows]
        result = json.dumps(result)
        print get_debug_queries()

        # If we're using a caching view
        # add the new key to the cache
        if cache:
            redis.set(search_term, result)

    return result


def build_query(search_term):
    """
    Build query string to pass to SQLAlchemy
    """
    formatted_search_term = '%{}%'.format(search_term)

    # Basic query that searches for recipes
    # whose names/ingredients match the search term
    query = """
        SELECT
            name,
            id,
            prep_time,
            cook_time,
            (substring(cook_time from '\d+')::int + substring(prep_time from '\d+')::int) as total_time,
            rating
        FROM
            recipe
        WHERE
            name like :search_term
            OR ingredients like :search_term
        """

    # If someone searches for '# mins', strip out
    # the text and cast the number string as an int.
    # Then query for recipes with a total time <= searched time
    try:
        int_search_term = int(search_term.strip(" mins").strip(" hours"))
    except ValueError:
        pass
    else:
        query += """
            OR {} >= (substring(cook_time from '\d+')::int + substring(prep_time from '\d+')::int)
        """.format(int_search_term)
    query += """
        ORDER BY
            name,
            rating DESC
        LIMIT 30
    """
    return query


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


if __name__ == '__main__':
    app.run(debug=True)
