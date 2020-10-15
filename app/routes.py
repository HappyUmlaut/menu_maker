from app import app
from app import db
from flask_login import current_user, login_user, logout_user
from app.models import User, Ingredient, Recipe, RecipePicture
from flask import redirect, flash, url_for, render_template, request, session
from app.forms import LoginForm, RegistrationForm
from sys import stderr
from werkzeug.utils import secure_filename
import os

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/new_menu')
def new_menu():
    return render_template('new_menu.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/new_recipe', methods=['GET', 'POST'])
def new_recipe():
    if request.method == "POST":
        # Get data from form
        data = request.form

        # Separate quantity and ingredient names, and save them to 
        # database if user is logged in, or to session if not
        if current_user.is_authenticated:
            username = current_user.username

            # Get recipe name
            recipe_name = data['recipe'];

            # Add recipe to database session
            recipe = Recipe(name = recipe_name, user = current_user)
            db.session.add(recipe)

            # Save ingredients in recipe dictionary
            for ingredient in data.values():
                # Pass recipe because it is not an ingredient
                if ingredient == recipe_name:
                    continue
                if ingredient.lower().endswith(('.png','.jpg')):
                    print('image found', file=stderr)
                    continue
                # Split in maximum 2 parts (quantity and name)
                quantity, name = ingredient.split(' ', 1)

                # Add ingredient to database session
                next_ingredient = Ingredient(name = name, quantity = quantity,
                                recipe = recipe)
                db.session.add(next_ingredient)

            # Check if an image was uploaded
            if 'image' in request.files and request.files['image'].filename != '':
                file = request.files['image']
                filename, extension = file.filename.split('.')
                file.filename = recipe_name + '_user-' + username + '.' + extension

                # Create a secure filename
                filename = secure_filename(file.filename)

                # Check if user directory for images exist. If not, create it
                if not os.path.isdir('app/static/images/recipe_images/' + username):
                    os.mkdir('app/static/images/recipe_images/' + username)

                # Save image
                file.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], username + '/'), filename))

                # Add image location to database
                file_location = '/images/recipe_images/' + username + '/' + filename

                # Add image to database
                image = RecipePicture(recipe = recipe, filename = file_location)

            else:
                file_location = '/images/recipe_images/image-placeholder.png'
                image = RecipePicture(recipe = recipe, filename = file_location)

            db.session.add(image)

            # Commit session to database
            db.session.commit()

            return redirect(url_for('index'))
        else:
            # Get recipe name
            recipe_name = data['recipe'];

            # Create dictionary for this recipe
            recipe = {}

            # Save ingredients in recipe dictionary
            for ingredient in data.values():
                # Pass recipe because it is not an ingredient
                if ingredient == recipe_name:
                    continue
                # Split in maximum 2 parts (quantity and name)
                quantity, name = ingredient.split(' ', 1)
                recipe[name] = quantity
            
            # Save recipe to session
            session[recipe_name] = recipe

            flash ('Recipe saved!')
            return redirect(url_for('index'))
    else:    
        return render_template('new_recipe.html')

@app.route('/recipes')
def show_recipes():
    if current_user.is_authenticated:
        # Get current user id
        user_id = current_user.get_id()

        # Get all recipes for current user
        recipes = db.session.query(Recipe.name).filter(Recipe.user_id==1).all()

        # Create dictionary to hold all ingredients for each recipe
        full_recipes = {}
        recipe_images = []
        # Since query returns a named tuple, unpack tuple in for loop to use recipe name directly
        for recipe, in recipes:
            full_recipes[recipe] = db.session.query(Ingredient.quantity, Ingredient.name).filter(Ingredient.recipe_id.in_(db.session.query(Recipe.id).filter(Recipe.name==recipe))).all()[0]

             # Get image for recipe
            recipe_images.append(db.session.query(RecipePicture.filename).filter(RecipePicture.recipe_id.in_(db.session.query(Recipe.id).filter(Recipe.name==recipe))).all()[0])

        print(recipe_images, file=stderr)

        return render_template('recipes.html', recipes=full_recipes, recipe_images = recipe_images)
    else:
        return render_template('recipes.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))