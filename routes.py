# from crypt import methods
from app import app, db
from models import (
    Cuisine,
    DislikedIngredients,
    DislikedRecipes,
    Ingredients,
    Intolerances,
    Recipes,
    User,
)
import os
import flask
from flask_login import login_user, current_user, LoginManager, logout_user
from flask_login.utils import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from spoonacular import *

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(username):
    return User.query.get(username)


@app.route("/")
def index():

    return flask.render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        uname = flask.request.form.get("username")
        password = flask.request.form.get("password")
        flask.session["currentUser"] = uname

        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password, password):
            # creates cookie and session
            login_user(user)
            return flask.redirect(flask.url_for("home"))
        else:
            flask.flash("The username or password is incorrect")

    return flask.render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "POST":
        uname = flask.request.form.get("username")
        password = flask.request.form.get("password")
        lname = flask.request.form.get("lastname")
        fname = flask.request.form.get("firstname")
        email = flask.request.form.get("email")

        user = User.query.filter_by(username=uname).first()
        if user:
            flask.flash("looks like this username is taken! please choose another one.")
            return flask.redirect(flask.url_for("register"))
        check_email = User.query.filter_by(email=email).first()
        if check_email:
            flask.flash(
                "looks like this email has an account already associated with it. Please enter another email"
            )
            return flask.redirect(flask.url_for("register"))
        user = User(
            username=uname,
            password=generate_password_hash(password),
            last_name=lname,
            first_name=fname,
            email=email,
        )
        print(user)
        db.session.add(user)
        db.session.commit()
        return flask.redirect(flask.url_for("login"))
    return flask.render_template("register.html")


@login_required
@app.route("/home")
def home():

    return flask.render_template("home.html")


@login_required
@app.route("/profile")
def profile():
    username = current_user.username
    likedRecipes = Recipes.query.filter_by(username=username)
    likedIngredients = Ingredients.query.filter_by(username=username)
    dislikedIngredients = DislikedIngredients.query.filter_by(username=username)
    dislikedRecipes = DislikedRecipes.query.filter_by(username=username)
    cuisine = Cuisine.query.filter_by(username=username)
    intolerance = Intolerances.query.filter_by(username=username)
    # print(likedRecipes)
    # DislikedIngredients = DislikedIngredients.query.filter_by(username=username)
    # dislikedIngredients = DislikedIngredients.query
    return flask.render_template(
        "profile.html",
        likedRecipes=likedRecipes,
        likedIngredients=likedIngredients,
        dislikedIngredients=dislikedIngredients,
        dislikedRecipes=dislikedRecipes,
        cuisine=cuisine,
        intolerance=intolerance,
    )


@app.route("/logout")
@login_required
def logout():

    # flask.session["currentUser"] = uname
    # current = flask.session.get("currentUser", None)
    logout_user()
    return flask.redirect(flask.url_for("login"))


@app.route("/search_recipes", methods=["POST", "GET"])
def search_recipes():
    recipeInfo = ""
    recipe = flask.request.form.get("recipe")
    recipe1 = recipe

    cuisine = flask.request.form.get("cuisine")
    intolerance = flask.request.form.get("intolerance")
    # print(cuisine)
    # print(intolerance)
    recipe1 += "," + cuisine
    # + "," + intolerance
    # print(recipe)
    if recipe:
        try:
            recipeInfo = get_recipe(recipe, intolerance)
            # , intolerance)
        except (IndexError, KeyError):
            flask.flash("sorry, that search could not be displayed. please try again.")
            # return flask.redirect(flask.url_for("home"))
    # recipe = recipe
    # print(recipeInfo)
    # print(recipeInfo[0]["name"])
    return flask.render_template("home.html", keyword=recipe, recipeInfo=recipeInfo)


@app.route("/search_ingredients", methods=["POST", "GET"])
def search_ingredients():
    ingredient = flask.request.form.get("ingredient")
    if ingredient:
        # try:
        ingredientInfo = get_ingredient(ingredient)
    # except (IndexError, KeyError):
    else:
        flask.flash("sorry, that search could not be displayed. please try again.")
        # return flask.redirect(flask.url_for("home"))
    # print(ingredientInfo)
    # recipe = recipe
    # print(ingredientInfo)
    # print(ingredientInfo[0]["name"])
    return flask.render_template(
        "home.html", keyword=ingredient, ingredientInfo=ingredientInfo
    )


@login_required
@app.route("/like_recipe", methods=["POST", "GET"])
def like_recipe():
    recipe = flask.request.form.get("recipeName")
    # image = flask.request.form.get("recipeImage")
    # cuisine = flask.request.form.get("cuisine")
    username = current_user.username
    user_id = current_user.get_id()

    # print(recipe, username, user_id)
    check = Recipes.query.filter_by(username=username).filter_by(recipe=recipe).first()
    if not check:
        db.session.add(
            Recipes(recipe=recipe, username=username, user_id=user_id)
            # , image=image)
        )
        db.session.commit()
        flask.flash("you have successfully liked " + recipe + " !")

    else:
        flask.flash("looks like you already liked that recipe!")
    return flask.render_template("home.html")


@login_required
@app.route("/dislike_recipe", methods=["POST", "GET"])
def dislike_recipe():
    recipe = flask.request.form.get("recipeName")
    # cuisine = flask.request.form.get("cuisine")
    username = current_user.username
    user_id = current_user.get_id()
    # print(recipe, username, user_id)
    check = (
        DislikedRecipes.query.filter_by(username=username)
        .filter_by(disliked_recipe=recipe)
        .first()
    )
    if not check:
        db.session.add(
            DislikedRecipes(disliked_recipe=recipe, username=username, user_id=user_id)
        )
        db.session.commit()
        flask.flash("you have successfully disliked " + recipe + " !")

    else:
        flask.flash("looks like you already disliked that recipe!")
    return flask.render_template("home.html")


@login_required
@app.route("/dislike_ingredient", methods=["POST", "GET"])
def dislike_ingredient():
    ingredient = flask.request.form.get("ingredientName")
    username = current_user.username
    user_id = current_user.get_id()
    # print(ingredient, username, user_id)
    check = (
        DislikedIngredients.query.filter_by(username=username)
        .filter_by(disliked_ingredient=ingredient)
        .first()
    )
    if not check:
        db.session.add(
            DislikedIngredients(
                disliked_ingredient=ingredient, username=username, user_id=user_id
            )
        )
        db.session.commit()
        flask.flash("you have successfully disliked " + ingredient + " !")
    else:
        flask.flash("looks like you already disliked that ingredient!")

    return flask.render_template("home.html")


@login_required
@app.route("/like_ingredient", methods=["POST", "GET"])
def like_ingredient():
    ingredient = flask.request.form.get("ingredientName")
    username = current_user.username
    user_id = current_user.get_id()
    # print(ingredient, username, user_id)
    check = (
        Ingredients.query.filter_by(username=username)
        .filter_by(ingredient=ingredient)
        .first()
    )
    if not check:
        db.session.add(
            Ingredients(ingredient=ingredient, username=username, user_id=user_id)
        )
        db.session.commit()
        flask.flash("you have successfully liked " + ingredient + " !")
    else:
        flask.flash("looks like you already liked that ingredient!")

    return flask.render_template("home.html")


@login_required
@app.route("/save_cuisines", methods=["POST", "GET"])
def save_cuisines():
    cuisine = flask.request.form.get("cuisine")
    username = current_user.username
    user_id = current_user.get_id()
    # print(ingredient, username, user_id)
    check = (
        Cuisine.query.filter_by(username=username).filter_by(cuisine=cuisine).first()
    )
    if not check:
        db.session.add(Cuisine(cuisine=cuisine, username=username, user_id=user_id))
        db.session.commit()
        flask.flash("you have successfully saved " + cuisine + " !")
    else:
        flask.flash("looks like you already saved that cuisine!")

    return flask.render_template("profile.html")


@login_required
@app.route("/save_intolerances", methods=["POST", "GET"])
def save_intolerance():
    intolerance = flask.request.form.get("intolerance")
    username = current_user.username
    user_id = current_user.get_id()
    # print(ingredient, username, user_id)
    check = (
        Intolerances.query.filter_by(username=username)
        .filter_by(intolerance=intolerance)
        .first()
    )
    if not check:
        db.session.add(
            Intolerances(intolerance=intolerance, username=username, user_id=user_id)
        )
        db.session.commit()
        flask.flash("you have successfully liked " + intolerance + " !")
    else:
        flask.flash("looks like you already saved that intolerance!")

    return flask.render_template("profile.html")


# @app.route("/bookList")
# def booklist():
#     likedRecipes = db.execute("SELECT * FROM booklist order by bookid")
#     return flask.render_template("profile.html", recipes=likedRecipes)


# app.run(debug=True)
if __name__ == "__main__":
    app.run(
        host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True
    )
    # app.init_app()
    # app.start_app()
