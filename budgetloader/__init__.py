from flask import Flask
from flask import render_template
from datetime import datetime, date, time
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import budgetloader.data
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    auth = HTTPBasicAuth()

    @auth.verify_password
    def verify_password(username, password):
        # Load the hash
        hash = ""
        with open("hash.txt", "r") as f:
            hash = f.readline()

        # Check the hash
        if check_password_hash(hash, password):
            return username

    @app.route("/")
    @auth.login_required
    def index():
        now = datetime.now()

        categories = data.get_categories(now.year, 3)
        transactions = data.get_transactions(now.year, 3)
        return render_template('index.html', month=3, categories=categories, transactions=transactions)

    @app.route("/category/<int:id>/edit")
    @auth.login_required
    def edit_category(id):
        category = data.get_category(id)
        if not category is None:
            return render_template('edit_category.html', category=category)
        else:
            return ""

    return app

app = create_app()