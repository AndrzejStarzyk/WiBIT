from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta

from display_route import create_map
from recommending_v2.categories.categories import categories
from recommending_v2.recommender import Recommender as EvalRecommender
from recommending_v2.model.constraint import *

app = Flask(__name__)

eval_recommender = EvalRecommender()


@app.route('/', methods=['GET', 'POST'])
def show_home():
    return render_template("home.html")


@app.route('/map')
def show_map():
    return render_template("choose_page.html", input_categories=categories)


@app.route('/duration', methods=['GET', 'POST'])
def show_duration():
    duration_options = [
        {'name': 'Jeden dzień', 'time': 1},
        {'name': 'Dwa dni', 'time': 2},
        {'name': 'Trzy dni', 'time': 3},
        {'name': 'Pięć dni', 'time': 5},
        {'name': 'Tydzień', 'time': 7},
    ]
    if request.method == 'POST':
        selected_option = request.form.get('duration_dropdown')
        eval_recommender.set_pois_limit(int(selected_option) * 3 + 10)
        eval_recommender.days = int(selected_option)
        return redirect(url_for('show_start_date'))

    return render_template('visit_duration_form.html', options=duration_options)


@app.route('/start_date', methods=['GET', 'POST'])
def show_start_date():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        return redirect(url_for('show_schedule', start=start_date))
    return render_template("choose_start_date.html", tomorrow=date.today() + timedelta(days=1))


@app.route('/schedule/<start>', methods=['GET', 'POST'])
def show_schedule(start: str):
    if request.method == 'POST':
        schedule_inputs = [[f"start_{i}", f"end_{i}"] for i in range(eval_recommender.days)]
        schedule_hours = [(request.form.get(schedule_inputs[i][0]), request.form.get(schedule_inputs[i][1]))
                          for i in range(0, len(schedule_inputs))]
        eval_recommender.hours = schedule_hours
        eval_recommender.create_schedule()
        return redirect(url_for('show_categories'))

    start_date = date.fromisoformat(start)
    dates = []
    for i in range(0, eval_recommender.days):
        tmp = start_date + timedelta(days=i)
        dates.append(tmp.isoformat())

    eval_recommender.dates = dates
    return render_template("schedule.html", dates=dates)


@app.route('/categories', methods=['GET', 'POST'])
def show_categories():
    return render_template("choose_page.html", input_categories=categories)


@app.route('/suggested', methods=['GET', 'POST'])
async def show_suggested():
    res = render_template("default_page.html")
    if request.method == 'GET':
        try:
            eval_recommender.set_pois_limit(7)
            eval_recommender.create_schedule()
            recommended = eval_recommender.get_recommended()

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
        init_pref = []
        for item in request.form.items():
            if item[0].startswith('button'):
                continue
            elif item[0].startswith('remove'):
                eval_recommender.add_constraint(AttractionConstraint([item[1]], False))
                eval_recommender.pois_limit -= 1
            elif item[0].startswith('replace'):
                eval_recommender.add_constraint(AttractionConstraint([item[1]], False))
            elif item[0].startswith('cat'):
                init_pref.append(item[1])
            elif item[0].startswith('datetime'):
                if item[0] == 'datetime_start':
                    pass
                if item[0] == 'datetime_end':
                    pass

        if len(init_pref) > 0:
            eval_recommender.add_constraint(CategoryConstraint(init_pref))

        eval_recommender.create_schedule()
        recommended = eval_recommender.get_recommended()
        m = create_map(recommended)
        m.get_root().render()
        res = render_template("suggested_page.html", places=recommended.pois,
                              map_header=m.get_root().header.render(),
                              map_html=m.get_root().html.render(),
                              map_script=m.get_root().script.render())
        return res

    return res


if __name__ == '__main__':
    app.run()

"""
    duration_options = [
        {'name': 'Jedno popołudnie', 'time': 2},
        {'name': 'Jeden dzień', 'time': 1},
        {'name': 'Weekend (2-3 dni)', 'time': 8},
        {'name': '4-5 dni', 'time': 15},
        {'name': 'Cały tydzień', 'time': 20},
    ]
"""
