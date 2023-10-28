from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta
from flask_bcrypt import Bcrypt
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from wtforms.validators import ValidationError

from display_route import create_map
from recommending_v2.algorythm_models.user_in_algorythm import User as Algo_User
from recommending_v2.recommender import Recommender
from recommending_v2.algorythm_models.constraint import *
from recommending_v2.algorythm_models.default_trip import DefaultTrip
from models.constants import SECRET_KEY
from models.objectid import PydanticObjectId
from models.forms import LoginForm, RegisterForm
from models.user import User
from models.mongo_utils import MongoUtils

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

algo_user = Algo_User()
categories_provider = CategoriesProvider()
default_trip = DefaultTrip()
recommender = Recommender(algo_user)

mongo_utils = MongoUtils()
users = mongo_utils.get_collection('users')
user_name = None


@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({"_id": PydanticObjectId(user_id)})
    return User(**user) if user else None


def update_user_name():
    global user_name
    if current_user.is_authenticated:
        user_name = current_user.login
    else:
        user_name = None


@app.route('/', methods=['GET', 'POST'])
def show_home():
    update_user_name()
    return render_template("home.html", user_name=user_name)


@app.route("/login", methods=['GET', 'POST'])
def login():
    alert = None
    form = LoginForm()
    if form.validate_on_submit():
        login_login = form.username.data
        login_password = form.password.data

        user = users.find_one({"login": login_login})
        if user is not None:
            curr_user = User(**user)
            if bcrypt.check_password_hash(curr_user.password, login_password):
                login_user(curr_user, duration=timedelta(days=1))
                update_user_name()
                return redirect(url_for('user_main_page'))
            else:
                alert = "Podano błędne hasło!"
        else:
            alert = "Taki użytkownik nie istnieje!"

    return render_template("authentication/login.html", form=form, alert_message=alert)


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    alert = None
    form = RegisterForm()
    if form.validate_on_submit():
        new_login = form.username.data
        new_pass_1 = form.password1.data
        new_pass_2 = form.password2.data

        if not users.find_one({"login": new_login}):
            if new_pass_1 == new_pass_2:
                hashed_password = bcrypt.generate_password_hash(new_pass_1.encode('utf-8'))

                cursor = users.find().sort("user_id", -1).limit(1)
                last_user = next(cursor, None)
                user_id = last_user["user_id"] + 1 if last_user else 1

                raw_usr = {"user_id": user_id,
                           "login": new_login,
                           "password": hashed_password}
                try:
                    user = User(**raw_usr)
                    users.insert_one(user.to_bson())

                    user = users.find_one({"login": new_login})
                    curr_user = User(**user)
                    login_user(curr_user, duration=timedelta(days=1))
                    update_user_name()
                    return redirect(url_for('show_home'))

                except ValidationError as e:
                    alert = "Wystąpił błąd podczas tworzenia konta!"
                    print(e)
            else:
                alert = "Podane hasła nie są takie same!"
        else:
            alert = "Ta nazwa użytkownika jest już zajęta!"

    return render_template("authentication/registration.html", form=form, alert_message=alert)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    global user_name
    user_name = None
    return redirect(url_for('show_home'))


@app.route('/duration', methods=['GET', 'POST'])
@login_required
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
        recommender.days = int(selected_option)
        return redirect(url_for('show_start_date'))

    return render_template('visit_duration_form.html', options=duration_options)


@app.route('/start_date', methods=['GET', 'POST'])
@login_required
def show_start_date():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        return redirect(url_for('show_schedule', start=start_date))
    return render_template("choose_start_date.html", tomorrow=date.today() + timedelta(days=1))


@app.route('/schedule/<start>', methods=['GET', 'POST'])
@login_required
def show_schedule(start: str):
    if request.method == 'POST':
        schedule_inputs = [[f"start_{i}", f"end_{i}"] for i in range(recommender.days)]
        schedule_hours = [(request.form.get(schedule_inputs[i][0]), request.form.get(schedule_inputs[i][1]))
                          for i in range(0, len(schedule_inputs))]
        recommender.hours = schedule_hours
        recommender.create_schedule()
        return redirect(url_for('show_categories'))

    start_date = date.fromisoformat(start)
    dates = []
    for i in range(0, recommender.days):
        tmp = start_date + timedelta(days=i)
        dates.append(tmp.isoformat())

    recommender.dates = dates
    return render_template("schedule.html", dates=dates)


@app.route('/categories', methods=['GET', 'POST'])
@login_required
def show_categories():
    if request.method == 'POST':
        categories = categories_provider.get_subcategories(list(map(lambda x: x[0][4:], request.form.items())))
        return render_template("choose_page.html", input_categories=categories, redirect='/suggested')
    categories = categories_provider.get_main_categories()
    return render_template("choose_page.html", input_categories=categories, redirect='/categories')


@app.route('/default_trip', methods=['GET'])
def show_default_trip():
    print("default")
    res = render_template("default_page.html")
    try:
        trajectory = default_trip.get_trip(None)
        m = create_map(trajectory)
        m.get_root().render()
        map_data = [(m.get_root().html.render(), m.get_root().script.render(), trajectory.get_pois())]
        res = render_template("suggested_page.html", trajectories_data=map_data,
                              map_headers=[m.get_root().header.render()])
    except FileExistsError:
        print("Index file no found")

    return res


def render_suggested_template():
    recommender.create_schedule()
    recommended = recommender.get_recommended()
    maps = [create_map(trajectory) for trajectory in recommended.trajectories]
    for m in maps:
        m.get_root().render()
    headers = [m.get_root().header.render() for m in maps]
    trajectories_data = [(maps[i].get_root().html.render(),
                          maps[i].get_root().script.render(),
                          recommended.trajectories[i].get_pois()) for i in range(len(recommended.trajectories))]

    res = render_template("suggested_page.html", trajectories_data=trajectories_data, map_headers=headers)
    return res


@app.route('/suggested', methods=['POST'])
@login_required
async def show_suggested():
    res = render_template("default_page.html")

    if request.method == "POST":
        init_pref = []
        for item in request.form.items():
            if item[0].startswith('button'):
                continue
            elif item[0].startswith('remove'):
                recommender.add_constraint(AttractionConstraint([item[1]], False))
                recommender.pois_limit -= 1
            elif item[0].startswith('replace'):
                recommender.add_constraint(AttractionConstraint([item[1]], False))
            elif item[0].startswith('cat'):
                init_pref.append(item[0][4:0])
            elif item[0].startswith('datetime'):
                if item[0] == 'datetime_start':
                    pass
                if item[0] == 'datetime_end':
                    pass

        if len(init_pref) > 0:
            recommender.add_constraint(CategoryConstraint(init_pref))

        return render_suggested_template()

    return res


@app.route('/user-panel', methods=['GET'])
def user_main_page():
    if current_user.is_authenticated:
        return render_template("user_main_page.html", user_name=current_user.login)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
