from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
    login_required,
)

import spoonacular_calls as spoon
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


# Association tables for many-to-many relationships
diet_preferences = db.Table(
    "diet_preferences",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("diet_id", db.Integer, db.ForeignKey("diet.id"), primary_key=True),
)

allergies_association = db.Table(
    "allergies_association",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("allergy_id", db.Integer, db.ForeignKey("allergy.id"), primary_key=True),
)

recipe_diets = db.Table(
    "recipe_diets",
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipe.id"), primary_key=True),
    db.Column("diet_id", db.Integer, db.ForeignKey("diet.id"), primary_key=True),
)

user_recipes = db.Table(
    "user_recipes",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipe.id"), primary_key=True),
)


# recipe-specific ingredient table. We need a full table because of storing ingredient quantities/units
class RecipeIngredient(db.Model):
    __tablename__ = "RecipeIngredient"
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), primary_key=True, autoincrement=False, nullable=False, default=0)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), primary_key=True, autoincrement=False, nullable=False, default=0)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(32), nullable=False)
    
    #orm stuff
    recipe = db.relationship("Recipe", back_populates="ingredients")
    ingredient = db.relationship("Ingredient", back_populates="recipes")

#user database table
class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    
    # Relationships
    diets = db.relationship(
        "Diet", secondary=diet_preferences, backref=db.backref("users", lazy="dynamic")
    )
    allergies = db.relationship(
        "Allergy",
        secondary=allergies_association,
        backref=db.backref("users", lazy="dynamic"),
    )
    recipes = db.relationship("Recipe", secondary=user_recipes, backref=db.backref("users", lazy="dynamic"))
    
    @property
    def has_filled_preferences(self):
        return bool(self.diets) or bool(self.allergies)

#diet database table
class Diet(db.Model):
    __tablename__ = "diet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)

#allergy database table
class Allergy(db.Model):
    __tablename__ = "allergy"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)

class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    spoonacular_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(250), unique=False, nullable=False)  # i think spoonacular might have duplicate recipe names
    description = db.Column(db.String)
    
    #relational ORM stuff (not part of schema)
    diets = db.relationship("Diet", secondary=recipe_diets, backref=db.backref("recipe", lazy="dynamic"))
    ingredients = db.relationship("RecipeIngredient", back_populates="recipe")
    
#ingredient database table
class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    spoonacular_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(250), unique=False, nullable=False) #i think spoonacular might have duplicate ingredient names
    
    #relational ORM stuff
    recipes = db.relationship("RecipeIngredient", back_populates="ingredient")
    


#NOTE: skipping allergies for now since spoonacular doesn't list them
#NOTE: recipe needs to store the recipe description, as well as amount per ingredient
#NOTE: if we have time, add an ingredient table with per-ingredient information (per serving?)


#TODO: test adding a recipe to the database
#TODO: write "recipes" html to display all recipes
#TODO: test adding a user-recipe relationship
#TODO: update "users" html to display user-recipe info
#TODO: add support for recipe nutrition (carb/fat/protein %, total calories, cook time)

with app.app_context():
    db.create_all()
    # Add initial diets if not already present
    if not Diet.query.first():
        diets = ["Vegetarian", "Vegan", "Gluten Free", "Keto", "Paleo"]
        for diet_name in diets:
            diet = Diet(name=diet_name)
            db.session.add(diet)
        db.session.commit()
    # Add initial allergies if not already present
    if not Allergy.query.first():
        allergies_list = [
            "Peanuts",
            "Tree Nuts",
            "Milk",
            "Eggs",
            "Shellfish",
            "Fish",
            "Soy",
            "Wheat",
        ]
        for allergy_name in allergies_list:
            allergy = Allergy(name=allergy_name)
            db.session.add(allergy)
        db.session.commit()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(
            username=request.form.get("username"), password=request.form.get("password")
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            # Use the new property to check preferences
            if not user.has_filled_preferences:
                return redirect(url_for("preferences"))
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add-recipe/test")
def recipe_test():
    return render_template("add_recipe.html")
    
@app.route("/add-recipe/spoonacular", methods=["POST"])
def add_recipe_spoonacular():
    ingredient_info = request.form.get('ingredient_info')
    if ingredient_info:
        data = spoon.RandomRecipe(1, True)
    else:
        data = spoon.RandomRecipe(1, False)
    add_recipe_to_database(data["recipes"][0])
    return data

@app.route("/add-recipe/json", methods=["POST"])
def add_recipe_json():
    filename = request.form.get('filename')
    data = None
    if filename:
        with open(filename, 'r') as file:
            data = json.load(file)
    add_recipe_to_database(data["recipes"][0])
    return data
    

def add_ingredient_to_database(ingredient):
    spoonacular_id = int(ingredient["id"])
    name = ingredient["name"]
    print(spoonacular_id)
    print(db.session.query(Ingredient).filter_by(spoonacular_id=spoonacular_id))
    existing_ingredient = db.session.query(Ingredient).filter_by(spoonacular_id=spoonacular_id).first()
    if existing_ingredient:
        existing_ingredient.name = name
    else:
        existing_ingredient = Ingredient(spoonacular_id=spoonacular_id, name=name)
        db.session.add(existing_ingredient)
    
    db.session.commit()
    return existing_ingredient

#NOTE: currently this function does NOT support ingredient-based nutrition information
#takes single recipe JSON and adds it to our database
def add_recipe_to_database(recipe):
    #TODO: only add to database if we haven't added it already
    spoonacular_id = recipe["id"]
    name = recipe["title"]
    description = recipe["summary"]
    diets = recipe["diets"]
    
    #for now, if a recipe already exists, we re-fill it completely
    exists = db.session.query(Recipe).filter_by(spoonacular_id=spoonacular_id).first()
    if exists:
        db_recipe = exists
        db_recipe.name = name
        db_recipe.description = description
    else:
        db_recipe = Recipe(spoonacular_id=spoonacular_id, name=name, description=description)
        db.session.add(db_recipe)
      
    #resetting diets and ingredients to be re-filled
    #TODO: db_recipe.diets...
    db.session.query(RecipeIngredient).filter_by(recipe_id=db_recipe.id).delete()
    
    #ADDING NUTRITION INFO
    if "nutrition" in recipe:
        nutrition = recipe["nutrition"]
        calories = 0 #TODO: this
        caloric_breakdown = nutrition["caloricBreakdown"]
    
    #ADD DIET INFO
    for diet in diets:
        pass
        #TODO: This
        #NOTE: you have to convert diet string to its id (query by string, get first matching diet ID
    
    #ADD INGREDIENT INFO
    ingredients = recipe["extendedIngredients"]
    
    #create ingredients if needed. build our array of ingredient IDs
    for ingredient in ingredients:
        #add ingredient
        ingredient_ref = add_ingredient_to_database(ingredient)
        #add association
        amount = float(ingredient["amount"])
        unit = ingredient["unit"]
        existing_ri = db.session.query(RecipeIngredient).filter_by(recipe_id=db_recipe.id, ingredient_id=ingredient_ref.id).first()
        
        if existing_ri:
            print(db_recipe.id)
            print(ingredient_ref.id)
            existing_ri.amount = amount
            existing_ri.unit = unit
        else:
            print(db_recipe.id)
            print(ingredient_ref.id)
            recipe_ingredient = RecipeIngredient(recipe_id=db_recipe.id, ingredient_id=ingredient_ref.id, quantity=amount, unit=unit)
            db.session.add(recipe_ingredient)
    db.session.commit()
    return db_recipe
      
      
    
    

@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    if request.method == "POST":
        # Get selected diet preferences and allergies from the form
        selected_diets = request.form.getlist("diets")
        selected_allergies = request.form.getlist("allergies")

        # Clear existing preferences
        current_user.diets = []
        current_user.allergies = []

        # Add new preferences
        for diet_id in selected_diets:
            diet = Diet.query.get(int(diet_id))
            if diet:
                current_user.diets.append(diet)
        for allergy_id in selected_allergies:
            allergy = Allergy.query.get(int(allergy_id))
            if allergy:
                current_user.allergies.append(allergy)

        db.session.commit()
        return redirect(url_for("home"))

    else:
        diets = Diet.query.all()
        allergies = Allergy.query.all()
        return render_template(
            "preferences.html", diets=diets, allergies=allergies, user=current_user
        )

@app.route('/users')
def show_users():
    users = Users.query.all()
    return render_template('users.html', users=users)

if __name__ == "__main__":
    app.run(debug=True)
