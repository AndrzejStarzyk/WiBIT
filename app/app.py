from flask import Flask, render_template, request, render_template_string
from reccomending_v1.display_route import create_map
from reccomending_v1.categories import categories
from reccomending_v1.recommending_similar_poi import Recommender
from recommending_v2.recommender import Recommender as EvalRecommender

app = Flask(__name__)
recommender = Recommender()
recommender.train()
eval_recommender = EvalRecommender()


@app.route('/')
def show_default():
    return render_template("choose_page.html", input_categories=categories)


@app.route('/map')
def show_map():
    res = render_template("default_page.html")
    try:
        selected = []
        for checkbox_result in request.values.lists():
            selected.append(checkbox_result[0])
        places = recommender.get_recommended(selected)
        create_map([(place['point']['lon'], place['point']['lat'], place['name']) for place in places])
        res = render_template("map.html")
    except FileExistsError:
        print("Index file no found")
    return res


@app.route('/suggested', methods=['GET', 'POST'])
def show_suggested():
    res = render_template("default_page.html")
    try:
        selected = []
        for checkbox_result in request.values.lists():
            selected.append(checkbox_result[0])
        recommended_places = recommender.get_recommended(selected)
        places_dicts = []

        for place in recommended_places:
            places_dicts.append({
                'name': place['name'],
                'xid': place['xid'],
                'kinds': place['kinds'].split(','),
                'lon': place['point']['lon'],
                'lat': place['point']['lat']
            })

        create_map([(place['lon'], place['lat'], place['name']) for place in places_dicts])

        res = render_template("suggested_page.html", places=places_dicts)
    except FileExistsError:
        print("Index file no found")
    return res


if __name__ == '__main__':
    app.run()
