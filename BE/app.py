from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from flask_cors import CORS

import spoonacular_calls as spoon
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
CORS(app)
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


banned_association = db.Table(
    "banned_association",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("ingredient_name", db.String(250), primary_key=True),
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
    instructions = db.Column(db.String)
    source_url = db.Column(db.String)
    fat_percent = db.Column(db.Float, default=33.3)
    carb_percent = db.Column(db.Float, default=33.3)
    protein_percent = db.Column(db.Float, default=33.3)
    calories = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float) #cost in cents (per serving)
    cook_time = db.Column(db.Integer) #in minutes
    servings = db.Column(db.Integer)
    
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
#NOTE: use DB Browser to look at current database status (no need for HTML printing it all)

#TODO: macros, total calories, and cook time for each recipe

#TODO: test adding a user-recipe relationship
#TODO: update "users" html to display user-recipe info

with app.app_context():
    db.create_all()
    print("Tables created:", db.metadata.tables.keys())

    # Add initial diets if not already present
    if not Diet.query.first():
        diets = ["None","Vegetarian","Lacto-Vegetarian","Ovo-Vegetarian","Vegan","Ketogenic","Gluten Free","Pescetarian","Paleo","Primal","Low FODMAP","Whole30"]
        for diet_name in diets:
            diet = Diet(name=diet_name)
            db.session.add(diet)
        db.session.commit()
    # Add initial allergies if not already present
    if not Allergy.query.first():
        allergies_list = [
            "Dairy",
            "Peanut",
            "Soy",
            "Egg",
            "Seafood",
            "Sulfite",
            "Gluten",
            "Sesame",
            "Tree Nut",
            "Grain",
            "Shellfish",
            "Wheat"
            
        ]
        for allergy_name in allergies_list:
            allergy = Allergy(name=allergy_name)
            db.session.add(allergy)
        db.session.commit()


@app.route("/api/recipes", methods=["GET"])
def getRecipes():
    #example
    return jsonify([
      {"id": 1, "name": 'Grilled Chicken Salad', "description": 'A healthy salad with grilled chicken and fresh veggies.'},
      {"id": 2, "name": 'Quinoa Bowl', "description": 'A nutritious quinoa bowl with mixed vegetables.'},
    ])

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
    spoonacular_id = recipe["id"]
    
    #for now, if a recipe already exists, we re-fill it completely
    exists = db.session.query(Recipe).filter_by(spoonacular_id=spoonacular_id).first()
    if exists:
        db_recipe = exists
    else:
        db_recipe = Recipe(spoonacular_id=spoonacular_id)
        db.session.add(db_recipe)
    
    #SETTING ALL BASIC VALUES
    db_recipe.name = recipe["title"]
    db_recipe.description = recipe["summary"]
    db_recipe.instructions = recipe["instructions"]
    db_recipe.source_url = recipe["sourceUrl"]
    db_recipe.cost = float(recipe["pricePerServing"])
    db_recipe.cook_time = int(recipe["readyInMinutes"])
    db_recipe.servings = int(recipe["servings"])
    
    #resetting ingredients to be re-filled
    db_recipe.diets = []
    db.session.query(RecipeIngredient).filter_by(recipe_id=db_recipe.id).delete()
    
    #TODO: everything in this if statement should be given a default value
    #ADDING NUTRITION INFO
    if "nutrition" in recipe:
        nutrition = recipe["nutrition"]
        caloric_breakdown = nutrition["caloricBreakdown"]
        db_recipe.fat_percent = float(caloric_breakdown["percentFat"])
        db_recipe.carb_percent = float(caloric_breakdown["percentCarbs"])
        db_recipe.protein_percent = float(caloric_breakdown["percentProtein"])
        for nutrient in nutrition["nutrients"]:
            nut_type = nutrient["name"]
            if nut_type == "Calories":
                db_recipe.calories = int(nutrient["amount"])
      
    #ADD DIET INFO
    diets = recipe["diets"]
    for diet in diets:
        #get diet ID from diet name
        curr_diet = db.session.query(Diet).filter_by(name=diet).first()
        if not curr_diet:
            curr_diet = Diet(name=diet)
            db.session.add(curr_diet)
        db_recipe.diets.append(curr_diet)
        
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
            existing_ri.amount = amount
            existing_ri.unit = unit
        else:
            recipe_ingredient = RecipeIngredient(recipe_id=db_recipe.id, ingredient_id=ingredient_ref.id, quantity=amount, unit=unit)
            db.session.add(recipe_ingredient)
    db.session.commit()
    return db_recipe
      
      
    
    

@app.route("/preferences", methods=["POST"])
@login_required
def preferences():

    data = request.get_json()  # Parse JSON payload

    if not data:
        return jsonify({"error": "No data provided"}), 400

    selected_diets = data.get("diet", [])
    selected_allergies = data.get("allergies", [])
    banned_ingredients_str = data.get("bannedIngredients", "")

    # Clear existing preferences
    current_user.diets = []
    current_user.allergies = []

    # Add new diet preferences
    for diet_name in selected_diets:
        diet = Diet.query.filter_by(name=diet_name).first()
        if diet:
            current_user.diets.append(diet)

    # Add new allergy preferences
    for allergy_name in selected_allergies:
        allergy = Allergy.query.filter_by(name=allergy_name).first()
        if allergy:
            current_user.allergies.append(allergy)

    # Parse and handle banned ingredients
    banned_ingredients = [ingredient.strip() for ingredient in banned_ingredients_str.split(",") if ingredient.strip()]

    # Clear existing banned ingredients
    db.session.execute(
        delete(banned_association).where(banned_association.c.user_id == current_user.id)
    )

    # Add new banned ingredients
    for ingredient in banned_ingredients:
        db.session.execute(
            banned_association.insert().values(user_id=current_user.id, ingredient_name=ingredient)
        )

    db.session.commit()

    return jsonify({
        "message": "Preferences updated successfully",
        "diets": [d.name for d in current_user.diets],
        "allergies": [a.name for a in current_user.allergies],
        "bannedIngredients": banned_ingredients,
    })

@app.route('/users')
def show_users():
    users = Users.query.all()
    return render_template('users.html', users=users)

if __name__ == "__main__":
    app.run(debug=True)
