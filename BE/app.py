from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
CORS(app)
db = SQLAlchemy(app)


class UserSettings(db.Model):
    __tablename__ = "user_settings"
    id = db.Column(db.Integer, primary_key=True)
    diets = db.Column(db.PickleType, default=[])
    allergies = db.Column(db.PickleType, default=[])
    banned_ingredients = db.Column(db.PickleType, default=[])


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String, nullable=True)
    instructions = db.Column(db.String, nullable=True)
    source_url = db.Column(db.String, nullable=True)
    fat_percent = db.Column(db.Float, default=33.3)
    carb_percent = db.Column(db.Float, default=33.3)
    protein_percent = db.Column(db.Float, default=33.3)
    calories = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float, default=0.0)
    cook_time = db.Column(db.Integer, default=0)
    servings = db.Column(db.Integer, default=1)


class MealPlan(db.Model):
    __tablename__ = "meal_plan"
    date = db.Column(db.String, primary_key=True)
    breakfast_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    lunch_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    dinner_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))

    breakfast = db.relationship("Recipe", foreign_keys=[breakfast_id])
    lunch = db.relationship("Recipe", foreign_keys=[lunch_id])
    dinner = db.relationship("Recipe", foreign_keys=[dinner_id])


with app.app_context():
    db.create_all()


@app.route("/user_settings", methods=["GET"])
def get_user_settings():
    user_settings = UserSettings.query.first()
    if not user_settings:
        return jsonify({"diets": [], "allergies": [], "bannedIngredients": []})
    return jsonify(
        {
            "diets": user_settings.diets,
            "allergies": user_settings.allergies,
            "bannedIngredients": user_settings.banned_ingredients,
        }
    )


@app.route("/user_settings", methods=["POST"])
def set_user_settings():
    data = request.get_json()
    user_settings = UserSettings.query.first()
    if not user_settings:
        user_settings = UserSettings()
        db.session.add(user_settings)

    user_settings.diets = data.get("diets", [])
    user_settings.allergies = data.get("allergies", [])
    user_settings.banned_ingredients = data.get("bannedIngredients", [])

    db.session.commit()
    return jsonify({"message": "User settings updated successfully"})


@app.route("/recipes", methods=["GET"])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify(
        [
            {
                "id": recipe.id,
                "name": recipe.name,
                "description": recipe.description,
                "instructions": recipe.instructions,
                "source_url": recipe.source_url,
                "fat_percent": recipe.fat_percent,
                "carb_percent": recipe.carb_percent,
                "protein_percent": recipe.protein_percent,
                "calories": recipe.calories,
                "cost": recipe.cost,
                "cook_time": recipe.cook_time,
                "servings": recipe.servings,
            }
            for recipe in recipes
        ]
    )


@app.route("/recipes/<int:id>", methods=["GET"])
def get_recipe(id):
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify(
        {
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "instructions": recipe.instructions,
            "source_url": recipe.source_url,
            "fat_percent": recipe.fat_percent,
            "carb_percent": recipe.carb_percent,
            "protein_percent": recipe.protein_percent,
            "calories": recipe.calories,
            "cost": recipe.cost,
            "cook_time": recipe.cook_time,
            "servings": recipe.servings,
        }
    )

@app.route("/recipes", methods=["POST"])
def add_recipe():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        recipe = Recipe(
            name=data.get("name"),
            description=data.get("description"),
            instructions=data.get("instructions"),
            source_url=data.get("source_url"),
            fat_percent=data.get("fat_percent", 0),
            carb_percent=data.get("carb_percent", 0),
            protein_percent=data.get("protein_percent", 0),
            calories=data.get("calories", 0),
            cost=data.get("cost", 0),
            cook_time=data.get("cook_time", 0),
            servings=data.get("servings", 0),
        )
        db.session.add(recipe)
        db.session.commit()
        return jsonify({"message": "Recipe added successfully", "recipe_id": recipe.id}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add recipe: {str(e)}"}), 500

@app.route("/mealplans/<date>", methods=["GET"])
def get_meal_plan(date):
    meal_plan = MealPlan.query.filter_by(date=date).first()
    if not meal_plan:
        return jsonify(None)
    return jsonify(
        {
            "date": meal_plan.date,
            "breakfast": {
                "id": meal_plan.breakfast.id,
                "name": meal_plan.breakfast.name,
                "description": meal_plan.breakfast.description,
            }
            if meal_plan.breakfast
            else None,
            "lunch": {
                "id": meal_plan.lunch.id,
                "name": meal_plan.lunch.name,
                "description": meal_plan.lunch.description,
            }
            if meal_plan.lunch
            else None,
            "dinner": {
                "id": meal_plan.dinner.id,
                "name": meal_plan.dinner.name,
                "description": meal_plan.dinner.description,
            }
            if meal_plan.dinner
            else None,
        }
    )


@app.route("/mealplans/<date>", methods=["POST"])
def set_meal_plan(date):
    data = request.get_json()
    meal_plan = MealPlan.query.filter_by(date=date).first()

    if not meal_plan:
        meal_plan = MealPlan(date=date)
        db.session.add(meal_plan)

    meal_plan.breakfast_id = data.get("breakfast_id")
    meal_plan.lunch_id = data.get("lunch_id")
    meal_plan.dinner_id = data.get("dinner_id")

    db.session.commit()
    return jsonify(
        {
            "message": f"Meal plan for {date} updated successfully",
            "date": meal_plan.date,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)