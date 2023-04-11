from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date, time
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from budgetloader import data, util, extraction
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
        # Set the year and month.
        if not request.args.get("year") is None:
            year = int(request.args["year"])
        else:
            year = datetime.now().year

        if not request.args.get("month") is None:
            month = int(request.args["month"])
        else:
            month = datetime.now().month

        # Retrieve the set month's totals and transactions.
        categories = data.get_categories(year, month)
        transactions = data.get_transactions(year, month)

        total_budget = sum(map(lambda cat: cat["budget"], categories))
        total_spent = sum(map(lambda cat: cat["total"], categories))

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
    @auth.login_required
    def update_category(id):
        category = {
            "id": id,
            "name": request.form["name"],
            "budget": request.form["budget"],
        }
        data.save_category(category)
        return redirect(url_for('index'))

    @app.route("/import", methods=["GET", "POST"])
    @auth.login_required
    def import_file():
        if request.method == "GET":
            return render_template('import.html')
        elif request.method == "POST":
            # Retrieve and save the file.
            file = request.files['upload']
            filename = secure_filename(file.filename)
            path = os.path.join(os.environ['BL_UPLOAD_PATH'], filename)
            
            # Check existence.
            # if os.path.exists(path):
            #     return redirect(url_for('import_file'))
            
            # Import the file.
            file.save(path)
            result = extraction.load_file(path)
            if result != "":
                return redirect(url_for('import_file'))
            
            # Going back to the home page means success.
            return redirect(url_for('index'))

    return app

app = create_app()
