from flask import Flask, render_template, request, redirect, url_for, abort, session
from datetime import date, timedelta
from flask_bcrypt import Bcrypt
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from wtforms.validators import ValidationError
from docx import Document
from pypdf import PdfReader
from odf import text, teletype
from odf.opendocument import load


from display_route import create_map
from recommending_v2.categories.estimated_visiting import VisitingTimeProvider
from recommending_v2.poi_provider import PoiProvider
from recommending_v2.algorythm_models.user_in_algorythm import User as Algo_User
from recommending_v2.recommender import Recommender
from recommending_v2.algorythm_models.constraint import *
from recommending_v2.algorythm_models.default_trip import DefaultTrip
from recommending_v2.algorythm_models.schedule import Schedule
from recommending_v2.save_trip import save_trip, schedule_from_saved_trip
from recommending_v2.algorythm_models.mongo_trip_models import TripDaysMongo
from recommending_v2.save_preferences import save_preferences, get_preferences_json, delete_preferences
from models.constants import SECRET_KEY
from models.objectid import PydanticObjectId
from models.forms import LoginForm, RegisterForm
from chatbot.chatbot_agent import ChatbotAgent
from models.user import User
from models.mongo_utils import MongoUtils

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

mongo_utils = MongoUtils()
chatbot_agent = ChatbotAgent()

users = mongo_utils.get_collection('users')
trips = mongo_utils.get_collection('trips')
user_name = None

algo_user = Algo_User()
categories_provider = CategoriesProvider(mongo_utils)
poi_provider = PoiProvider(mongo_utils)
visiting_time_provider = VisitingTimeProvider(mongo_utils)
default_trip = DefaultTrip(mongo_utils)
recommender = Recommender(algo_user, poi_provider, visiting_time_provider, default_trip)


@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({"_id": PydanticObjectId(user_id)})
    return User(**user) if user else None


def update_user_name():
    global user_name
    if current_user.is_authenticated:
        session['user_name'] = current_user.login
        user_name = current_user.login
    else:
        session.pop('user_name', None)
        user_name = None


@app.route('/', methods=['GET', 'POST'])
def show_home():
    update_user_name()
    return render_template("home.html", user_name=user_name)


@app.errorhandler(401)
def page_not_found(error):
    return render_template('error_template/unauth_error.html'), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error_template/default_error.html', communicate='404 - szukana strona nie istnieje'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error_template/default_error.html', communicate='500 - wystąpił problem z serwerem'), 500


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
    update_user_name()
    return redirect(url_for('show_home'))


@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def edit_preferences():
    user_preferences = get_preferences_json(current_user.id, mongo_utils)
    if request.method == 'POST':
        new_preferences: List[str] = []
        for item in request.form.items():
            if item[0].startswith('button'):
                continue
            elif item[0].startswith('cat'):
                new_preferences.append(item[0][4:])

        if len(new_preferences) > 0:
            save_preferences(current_user.id, [CategoryConstraint(new_preferences, mongo_utils)], mongo_utils)
        else:
            delete_preferences(current_user.id, mongo_utils)
        return redirect(url_for('user_main_page'))

    selected_codes = []
    for pref in user_preferences:
        if pref['constraint_type'] == ConstraintType.Category.value:
            for code in pref['value']:
                selected_codes.append(code)

    categories = [{
        'main': cat,
        'selected': cat.code in selected_codes,
        'sub': [{'category': sub, 'selected': sub.code in selected_codes} for sub in
                categories_provider.get_subcategories([cat.code])]
    } for cat in categories_provider.get_main_categories()]
    return render_template('edit_preferences.html', categories=categories, redirect='/preferences')


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
        recommender.days = int(selected_option)
        return redirect(url_for('show_start_date'))

    return render_template('creating_trip/visit_duration_form.html', options=duration_options)


@app.route('/start_date', methods=['GET', 'POST'])
def show_start_date():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        return redirect(url_for('show_schedule', start=start_date))
    return render_template("creating_trip/choose_start_date.html", tomorrow=date.today() + timedelta(days=1))


@app.route('/schedule/<start>', methods=['GET', 'POST'])
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
    return render_template("creating_trip/schedule.html", dates=dates)


@app.route('/categories', methods=['GET', 'POST'])
def show_categories():
    if request.method == 'POST':
        categories = categories_provider.get_subcategories(list(map(lambda x: x[0][4:], request.form.items())))
        return render_template("creating_trip/choose_page.html", input_categories=categories, redirect='/suggested')
    categories = categories_provider.get_main_categories()
    return render_template("creating_trip/choose_page.html", input_categories=categories, redirect='/categories')


@app.route('/default_trip', methods=['GET'])
def show_default_trip():
    res = render_template("default_page.html")
    try:
        trajectory = default_trip.get_trip(None)
        m = create_map(trajectory)
        m.get_root().render()
        map_data = [(m.get_root().html.render(), m.get_root().script.render(), trajectory.get_pois())]
        res = render_template("creating_trip/suggested_page.html", trajectories_data=map_data,
                              map_headers=[m.get_root().header.render()])
    except FileExistsError:
        print("Index file no found")

    return res


@app.route('/chatbot', methods=['GET', 'POST'])
def show_chatbot():
    if request.method == "POST":
        new_message = request.form['user_text']
        chatbot_agent.add_user_message(new_message)

        if chatbot_agent.is_finished and current_user.is_authenticated:
            chatbot_agent.save_text_prefs(mongo_utils=mongo_utils, user_id=current_user.id)

    chat_user = 'Użytkownik'
    if current_user.is_authenticated:
        chat_user = current_user.login
    return render_template("chatbot_view.html",
                           user_name=chat_user,
                           messages=chatbot_agent.get_all_messages(),
                           is_finished=chatbot_agent.is_finished)


@app.route('/reset-chatbot', methods=['POST'])
def restart_chatbot():
    global chatbot_agent
    chatbot_agent = ChatbotAgent()
    return redirect(url_for('show_chatbot'))


def render_trip(schedule: Schedule, template: str):
    maps = [create_map(trajectory) for trajectory in schedule.trajectories]
    for m in maps:
        m.get_root().render()
    headers = [m.get_root().header.render() for m in maps]
    trajectories_data = [(maps[i].get_root().html.render(),
                          maps[i].get_root().script.render(),
                          schedule.trajectories[i].get_pois()) for i in range(len(schedule.trajectories))]

    res = render_template(template, trajectories_data=trajectories_data,
                          map_headers=headers,
                          is_auth=current_user.is_authenticated)
    return res


@app.route('/suggested', methods=['POST'])
async def show_suggested():
    res = render_template("default_page.html")

    if request.method == "POST":
        temporary_pref = []
        for item in request.form.items():
            if item[0].startswith('button'):
                continue
            elif item[0].startswith('cat'):
                temporary_pref.append(item[0][4:])

        if len(temporary_pref) > 0:
            recommender.add_constraint(CategoryConstraint(temporary_pref, mongo_utils))

        if current_user.is_authenticated:
            user_pref = get_preferences_json(current_user.id, mongo_utils)
            for pref in user_pref:
                if pref['constraint_type'] == ConstraintType.Category.value:
                    recommender.add_constraint(CategoryConstraint(pref['value'], mongo_utils))
                if pref['constraint_type'] == ConstraintType.Attraction.value:
                    recommender.add_constraint(AttractionConstraint(pref['value']))
        recommender.create_schedule()
        recommended = recommender.get_recommended()
        return render_trip(recommended, "creating_trip/suggested_page.html")

    return res


@app.route('/suggest_again/<int:day_nr>', methods=['POST'])
def suggest_again(day_nr: int):
    some_removed = False
    some_replaced = False
    to_remove = []
    print(list(request.form.items()))
    for item in request.form.items():
        if item[0].startswith('button'):
            continue
        elif item[0].startswith('remove'):
            recommender.add_constraint(AttractionConstraint([item[1]], False))
            some_removed = True
            to_remove.append(item[1])
        elif item[0].startswith('replace'):
            recommender.add_constraint(AttractionConstraint([item[1]], False))
            some_replaced = True
    if some_removed and not some_replaced:
        recommended = recommender.remove_from_schedule(day_nr - 1, to_remove)
    elif not some_removed and not some_replaced:
        recommender.modify_general_constraint()
        recommended = recommender.recommend_again(day_nr - 1)
    else:
        recommended = recommender.recommend_again(day_nr - 1)
    return render_trip(recommended, "creating_trip/suggested_page.html")


# this is only API-endpoint
@app.route('/save-trip', methods=['POST'])
@login_required
def save_trip_route():
    save_trip(current_user.id, recommender.get_recommended())
    return 'saved'


@app.route('/user-panel', methods=['GET'])
@login_required
def user_main_page():
    if current_user.is_authenticated:
        return render_template("user_main_page.html", user_name=current_user.login)
    return redirect(url_for('login'))


@app.route('/saved', methods=['GET'])
@login_required
def all_saved_trips():
    user_trips_cursor = trips.find({'user_id': current_user.id})
    trip_minis = []

    for raw_trip in user_trips_cursor:
        trip = TripDaysMongo(**raw_trip)
        trip_mini = {
            'trip_id': trip.id,
            'date_start': trip.days[0].schedule.date,
            'date_end': trip.days[-1].schedule.date,
            'attractions_num': sum([len(trip.days[i].trajectory) for i in range(len(trip.days))])
        }

        trip_minis.append(trip_mini)

    trip_minis.reverse()

    return render_template('saved_trips.html', trips=trip_minis)


@app.route('/saved-trip', methods=['GET'])
@login_required
def saved_trip_page():
    trip_id = request.args.get('trip_id')

    raw_trip = trips.find_one({
        '_id': PydanticObjectId(trip_id),
        'user_id': current_user.id
    })

    if not raw_trip:
        abort(404)

    trip = TripDaysMongo(**raw_trip)

    return render_trip(schedule_from_saved_trip(trip), "saved_trip_page.html")


@app.route("/upload-file", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        added_file = request.files.get('file')
        if added_file:
            file_content = ""
            if added_file.filename.endswith('.txt'):
                file_content = added_file.read().decode('utf-8')

            elif added_file.filename.endswith('.pdf'):
                reader = PdfReader(added_file)
                number_of_pages = len(reader.pages)
                for i in range(number_of_pages):
                    page = reader.pages[0]
                    file_content += ' ' + page.extract_text()

            elif added_file.filename.endswith(('.docx', '.doc')):
                doc = Document(added_file)
                for paragraph in doc.paragraphs:
                    file_content += ' ' + paragraph.text
                pass

            elif added_file.filename.endswith('.odt'):
                odt_document = load(added_file)
                all_text_elements = odt_document.getElementsByType(text.P)
                for text_element in all_text_elements:
                    file_content += ' ' + teletype.extractText(text_element)

            print(file_content)

    return render_template("file_upload/file_upload.html")


if __name__ == '__main__':
    app.run()
