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

        budget_surplus = sum(map(lambda cat: cat["budget"], categories))
        total_spent = sum(map(lambda cat: cat["total"], categories))
        total_leftover = sum(map(lambda cat: cat["leftover"], categories))

        display_categories = map(lambda cat: {
            "id": cat["id"], 
            "name": cat["name"], 
            "budget": abs(util.to_dollars(cat["budget"])), 
            "total": abs(util.to_dollars(cat["total"])), 
            "leftover": util.to_dollars(cat["leftover"])
        }, categories)
        return render_template('index.html', month=4, categories=display_categories, transactions=transactions, budget_surplus=util.to_dollars(budget_surplus), total_spent=-util.to_dollars(total_spent), total_leftover=util.to_dollars(total_leftover))

    @app.route("/category/<int:id>/edit")
    @auth.login_required
    def edit_category(id):
        category = data.get_category(id)
        category["budget"] = util.to_dollars(category["budget"])
        if not category is None:
            return render_template('edit_category.html', category=category)
        else:
            return redirect(url_for('index'))
        
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
            
            # Import the file.
            file.save(path)
            result = extraction.load_file(path)
            if result != "":
                return redirect(url_for('import_file'))
            
            # Going back to the home page means success.
            return redirect(url_for('index'))

    # View patterns or create a new pattern.
    @app.route("/pattern", methods=["GET"])
    @auth.login_required
    def get_patterns():
        # Retrieve all patterns
        patterns = data.get_patterns()
        categories = data.get_all_categories()
        return render_template('pattern.html', patterns=patterns, categories=categories)

    # Edit a pattern.
    @app.route("/pattern/<int:id>/edit", methods=["GET"])
    @auth.login_required
    def edit_pattern(id):
        pattern = data.get_pattern(id)
        categories = data.get_all_categories()
        if not pattern is None:
            return render_template('edit_pattern.html', pattern=pattern, categories=categories)
        else:
            return redirect(url_for('get_patterns'))
        
    # Save a pattern.
    @app.route("/pattern/<int:id>", methods=["POST"])
    @auth.login_required
    def update_pattern(id):
        pattern = {
            "id": id,
            "regex": request.form["regex"],
            "category_id": request.form["category_id"],
            "precedence": request.form["precedence"],
        }
        data.save_pattern(pattern)
        return redirect(url_for('get_patterns'))

    @app.route("/pattern", methods=["POST"])
    @auth.login_required
    def add_pattern():
        pattern = {
            "id": None, # This will create one.
            "regex": request.form["regex"],
            "category_id": request.form["category_id"],
            "precedence": request.form["precedence"],
        }
        data.save_pattern(pattern)
        return redirect(url_for('get_patterns'))

    return app

app = create_app()
