# import necessary libraries
import os
from sqlalchemy.sql import select, column, text
from sqlalchemy.sql.expression import func
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
from models import create_classes
import simplejson
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', '') or "sqlite:///db.sqlite"


# Remove tracking modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

"""
To tell SQLAlchemy we’re lazy and it should teach 
itself about the database, we use this line:
"""
"""
It’s always the same, never changes. A million tables, weird names, etc etc, 
nothing affects it. If you don’t want to list all those columns out, you’ll be using that line.
"""

Breweries = create_classes(db)

# set up our route to use that template
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/mapping')
def v_timestamp():
    return render_template('mapping.html')

@app.route("/api")
def all():
    """
    list out all the dictionary
    """
    results = db.session.query(
        Breweries.name,
        Breweries.brewery_type,
        Breweries.address,
        Breweries.state,
        Breweries.phone,
        Breweries.website_url,
        Breweries.country,
        Breweries.region,
        Breweries.division,
        Breweries.longitude,
        Breweries.latitude
    ).all()

    return jsonify(results)

def get_selected_region():
    """
    Extracting the value from the query string (/?region=West -> West)
    """
    selected_region = request.args.get("region")

    # Ignore filtering if user selected "All"
    if selected_region == "All":
        return None
    
    #Make sure the selection in the proper title cased (west -> West)
    if selected_region is not None:
        selected_region = selected_region.title()
    
    return selected_region

@app.route("/api/count_by_region")
def count_by_region():
    """
    Count the number of breweries and groupby region
    """
    """ 
    {"region": "Midwest", 
    "total": 1292}
    """
    results = db.session.query(
        Breweries.region,
        func.count(Breweries.region).label("total")
    )

    results = results.group_by(
        Breweries.region
    ).all()

    return jsonify(results)

@app.route("/api/count_by/<count_by>", defaults={'optional_count_by': None})
@app.route("/api/count_by/<count_by>/<optional_count_by>")
def count_by(count_by, optional_count_by=None):
    """
    {"region": "Midwest", 
    "total": 1292}
    """
    """
    {"brewery_type": "brewpub", 
    "region": "Midwest", 
    "total": 561}
    """
    # check is there any existing filter
    selected_region = get_selected_region()
   
    # Only count_by (/api/count_by/<count_by>)
    if optional_count_by is None:
        results = db.session.query(
            getattr(Breweries, count_by),
            func.count(getattr(Breweries, count_by)).label("total")
        )

        # apply the query stirng filter if present
        if selected_region is not None:
            results = results.filter(Breweries.region == selected_region)

        results = results.group_by(
            getattr(Breweries, count_by)
        ).order_by(
            getattr(Breweries, count_by)
        ).all()

    else:
        # lets handle grouping by two columns
        results = db.session.query(
            getattr(Breweries, count_by),
            getattr(Breweries, optional_count_by),
            func.count(getattr(Breweries, count_by)).label("total")
        )

        if selected_region is not None:
            results = results.filter(Breweries.region == selected_region)

        results = results.group_by(
            getattr(Breweries, count_by),
            getattr(Breweries, optional_count_by)
        ).order_by(
            getattr(Breweries, count_by),
            getattr(Breweries, optional_count_by),
        ).all()

    return jsonify(results)


def get_column_values(for_column, selected_region = None):
    """
    get unique distinct values from column, filtering by query string
    """
    
    value_query = db.session.query(
        func.distinct(getattr(Breweries, for_column))
    )

    if selected_region is not None:
        value_query = value_query.filter(
            Breweries.region == selected_region
        )
    
    values = sorted([x[0] for x in value_query.all()])

    return values

@app.route("/api/values/<for_column>/<group_by>")
@app.route("/api/values/<for_column>/", defaults={'group_by': None})
def values(for_column, group_by = None):
    """
    group by the selected value with other column

    For example http://localhost:5000/api/values/region/
    [
     "Midwest", 
     "Northeast", 
     "South", 
     "West"
    ]

    Whereas http://localhost:5000/api/values/region/brewery_type
    """

    selected_region = get_selected_region()

    if group_by is None:
        values = get_column_values(for_column, selected_region)
        return jsonify(values)

    values_for_groupby = dict()

    group_by_values = get_column_values(group_by, selected_region)

    results = db.session.query(
        getattr(Breweries, group_by),
        getattr(Breweries, for_column),
    )

    if selected_region is not None:
        results = results.filter(
            Breweries.region, selected_region
        )

    results = results.order_by(
        getattr(Breweries, group_by),
        getattr(Breweries, for_column),
    ).all()

    for group in group_by_values:
        values_for_groupby[group] = [x[1] for x in results if x[0] == group]

    return jsonify(values_for_groupby)


@app.route("/api/where/<region>")
def where(region):
    """
    list out the relevant information with the input region
    """
    """
    {"address": "62950 NE 18th St Bend Oregon 97701", 
    "brewery_type": "large", 
    "country": "United States", 
    "division": "Pacific", 
    "id": 2, 
    "latitude": 44.0912109, 
    "longitude": -121.2809536, 
    "name": "10 Barrel Brewing Co - Bend Pub", 
    "phone": "5415851007", 
    "region": "West", 
    "state": "Oregon", 
    "website_url": "Not Available"}
    """
    results = db.engine.execute(text("""
        SELECT * FROM breweries 
        WHERE UPPER(region) = :region
    """).bindparams(
        region=region.upper().strip()
    ))

    return jsonify([dict(row) for row in results])

if __name__ == '__main__':
    app.run(debug=True)

