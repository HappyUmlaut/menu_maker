from app import db
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_imageattach.entity import Image, image_attachment

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)
    picture = db.relationship('RecipePicture', backref='recipe')

    def __repr__(self):
        return '<Recipe: %r>' % self.name

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

    def __repr__(self):
        return 'f<Ingredient: {self.name} | Quantity: {self.quantity} >'

class RecipePicture(db.Model):
    """Recipe picture model."""

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    filename = db.Column(db.String(255))
    __tablename__ = 'recipe_picture'
    def __repr__(self):
        return '<Filename: %r>' % self.filename
