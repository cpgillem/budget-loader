from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date, time
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from budgetloader import data, util
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

        categories = data.get_categories(now.year, 4)
        transactions = data.get_transactions(now.year, 4)

        total_budget = sum(map(lambda cat: cat["budget"], categories))
        total_spent = sum(map(lambda cat: cat["total"], categories))
        # total_leftover = sum(map(lambda cat: cat["leftover"], categories))
        # total_leftover = total_budget - total_spent

        display_categories = map(lambda cat: {
            "id": cat["id"], 
            "name": cat["name"], 
            "budget": abs(util.to_dollars(cat["budget"])), 
            "total": abs(util.to_dollars(cat["total"])), 
            "leftover": util.to_dollars(cat["leftover"])
        }, categories)
        return render_template('index.html', month=4, categories=display_categories, transactions=transactions, total_budget=util.to_dollars(total_budget), total_spent=util.to_dollars(total_spent))

    @app.route("/category/<int:id>/edit")
    @auth.login_required
    def edit_category(id):
        category = data.get_category(id)
        category["budget"] = util.to_dollars(category["budget"])
        if not category is None:
            return render_template('edit_category.html', category=category)
        else:
            return ""
        
    @app.route("/category/<int:id>", methods=["POST"])
    def update_category(id):
        category = {
            "id": id,
            "name": request.form["name"],
            "budget": request.form["budget"],
        }
        data.save_category(category)
        return redirect(url_for('index'))

    return app

app = create_app()