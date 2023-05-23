from flask import Flask, render_template, request
from display_route import create_map
from categories import categories
from recommending_similar_poi import Recommender

app = Flask(__name__)
recommender = Recommender()
recommender.train()

@app.route('/')
def show_default():
    return render_template("choose_page.html", categories=categories)


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


if __name__ == '__main__':
    app.run()
