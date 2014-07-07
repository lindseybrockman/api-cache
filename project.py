import json

from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
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
    return render_template('recipe.html', recipe_id=recipe_id, recipes=recipes)


@app.route('/autocomplete/recipe/', defaults={'search_term': ''}, methods=['GET', 'POST'])
@app.route('/autocomplete/recipe/<search_term>', methods=['GET'])
def autocomplete(search_term):
    """
    Autocomplete API
    """
    if request.method == 'POST':
        search_term = request.form['query']
    search_term = '%{}%'.format(search_term)
    query = """
        SELECT
            DISTINCT ON (name) name,
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
    try:
        search_time = int(search_term.replace('%', '').strip(" mins").strip(" hours"))
    except ValueError:
        pass
    else:
        query += """
            OR {} >= (substring(cook_time from '\d+')::int + substring(prep_time from '\d+')::int)
        """.format(search_time)
    query += """
        ORDER BY
            name,
            rating DESC
        LIMIT 30
    """
    cursor = db.engine.execute(text(query), search_term=search_term)
    rows = cursor.fetchall()
    columns = cursor.keys()
    result = [dict(zip(columns, row)) for row in rows]
    return json.dumps(result)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


if __name__ == '__main__':
    app.run(debug=True)
