from app import app
from app import db
from flask_login import current_user, login_user, logout_user
from app.models import User, Ingredient
from flask import redirect, flash, url_for, render_template, request, session
from app.forms import LoginForm, RegistrationForm
from sys import stderr

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

@app.route('/new_recipe', methods=['GET', 'POST'])
def new_recipe():
    if request.method == "POST":
        # Get data from form
        data = request.form

        # Separate quantity and ingredient names, and save them to 
        # database if user is logged in, or to session if not
        if current_user.is_authenticated:
            # Get recipe name
            recipe_name = data['recipe'];

            # Save ingredients in recipe dictionary
            for ingredient in data.values():
                # Pass recipe because it is not an ingredient
                if ingredient == recipe_name:
                    continue
                # Split in maximum 2 parts (quantity and name)
                quantity, name = ingredient.split(' ', 1)

                # Add ingredient to database session
                next_ingredient = Ingredient(recipe_name = recipe_name, 
                                ingredient_name = name, quantity = quantity,
                                user = current_user)
                db.session.add(next_ingredient)

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
    return render_template('recipes.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))