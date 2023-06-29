from flask import Flask, render_template, request, url_for, redirect

from reccomending_v1.display_route import create_map
from reccomending_v1.categories import categories
from reccomending_v1.recommending_similar_poi import Recommender
from recommending_v2.recommender import Recommender as EvalRecommender
from recommending_v2.model.constraint import *


app = Flask(__name__)
# recommender = Recommender()
# recommender.train()

eval_recommender = EvalRecommender()
#eval_recommender.add_constraint(AttractionConstraint(["N278057698"]), 5)
#eval_recommender.add_constraint(CategoryConstraint(["natural"]), 1)


@app.route('/')
def show_home():
    return render_template("home.html")


@app.route('/categories')
def show_categories():
    return render_template("choose_page.html", input_categories=categories)

@app.route('/map')
def show_map():
    res = render_template("default_page.html")
    """try:
        selected = []
        for checkbox_result in request.values.lists():
            selected.append(checkbox_result[0])
        places = recommender.get_recommended(selected)
        create_map([(place['point']['lon'], place['point']['lat'], place['name']) for place in places])
        res = render_template("map.html")
    except FileExistsError:
        print("Index file no found")"""
    return res


@app.route('/suggested', methods=['GET', 'POST'])
async def show_suggested():
    res = render_template("default_page.html")
    if request.method == 'GET':
        try:

            recommended = eval_recommender.get_recommended()
            eval_recommender.set_pois_limit(7)

            m = create_map(recommended)
            m.get_root().render()
            res = render_template("suggested_page.html", places=recommended.pois,
                                  map_header=m.get_root().header.render(),
                                  map_html=m.get_root().html.render(),
                                  map_script=m.get_root().script.render())
        except FileExistsError:
            print("Index file no found")
        return res

    if request.method == "POST":
        for item in request.form.items():
            if item[0] == "disabled":
                continue
            eval_recommender.add_constraint(AttractionConstraint([item[0]]))

        recommended = eval_recommender.get_recommended()
        m = create_map(recommended)
        m.get_root().render()
        res = render_template("suggested_page.html", places=recommended.pois,
                              map_header=m.get_root().header.render(),
                              map_html=m.get_root().html.render(),
                              map_script=m.get_root().script.render())
        return res

    return res


@app.route('/duration', methods=['GET', 'POST'])
def show_duration():
    duration_options = [
        {'name': 'Jedno popołudnie', 'time': 2},
        {'name': 'Jeden dzień', 'time': 4},
        {'name': 'Weekend (2-3 dni)', 'time': 8},
        {'name': '4-5 dni', 'time': 15},
        {'name': 'Cały tydzień', 'time': 20},
    ]

    if request.method == 'POST':
        selected_option = request.form.get('duration_dropdown')
        eval_recommender.set_pois_limit(int(selected_option))

        return redirect(url_for('show_categories'))

    return render_template('visit_duration_form.html', options=duration_options)


def remove_poi(xid: str):
    print(xid)


if __name__ == '__main__':
    app.run(debug=True)
