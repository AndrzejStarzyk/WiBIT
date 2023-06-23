from flask import Flask, render_template, request
from display_route import create_map
from categories import categories
from recommending_similar_poi import Recommender
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
        create_map(eval_recommender.get_recommended())
        res = render_template("suggested_page.html")
    except FileExistsError:
        print("Index file no found")
    return res


if __name__ == '__main__':
    app.run()
