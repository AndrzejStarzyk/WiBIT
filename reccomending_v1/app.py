from flask import Flask, render_template
from display_route import create_map

app = Flask(__name__)


@app.route('/')
def show_map():  # put application's code here
    res = render_template("default_page.html")
    try:
        create_map([])
        res = render_template("index.html")
    except FileExistsError:
        print("Index file no found")
    return res


if __name__ == '__main__':
    app.run()
