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
    @property
    def has_filled_preferences(self):
        return bool(self.diets) or bool(self.allergies)


class Diet(db.Model):
    __tablename__ = "diet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)


class Allergy(db.Model):
    __tablename__ = "allergy"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)


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
