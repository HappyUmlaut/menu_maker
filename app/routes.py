from app import app
from app import db
from flask_login import current_user, login_user, logout_user
from app.models import User, Ingredient, Recipe, RecipePicture, Menu
from flask import redirect, flash, url_for, render_template, request, session
from app.forms import LoginForm, RegistrationForm
from sys import stderr
from random import randint, shuffle
from werkzeug.utils import secure_filename
from numbers import Number
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
            flash('Invalid username or password', 'alert alert-danger')
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
        flash('You are now registered. You can now log in to your account', 'no-margin alert alert-success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/menus', methods=['GET', 'POST'])
def new_menu():
    user_menus = get_user_menus()
    # List with week days to pass to the template
    week = ['Monday', 'Thursday', 'Wednesday', 'Tuesday', 'Friday', 'Saturday', 'Sunday']

    if request.method == 'POST':
        if request.form['submit-button'] == 'new-menu':
            menu = create_menu()
            if current_user.is_authenticated:
                menu.user = current_user
                db.session.add(menu)
                db.session.commit()
                return redirect(url_for('new_menu'))
        else:
            # Get info from form to know which button was pressed, and delete that menu
            id_to_delete = request.form['submit-button']
            delete_menu(id_to_delete)
            return redirect(url_for('new_menu'))

    if current_user.is_authenticated:

        # List to hold existing menus, which are dictionaries
        menus = []

        for menu in user_menus:
            # Dictionary to hold recipes and their images
            current_menu = {}
            for recipe_id in menu:
                if 'id' not in current_menu:
                    # The first item contains the menu id from the database
                    current_menu['id'] = recipe_id
                    continue

                # Get data for every recipe in the curren menu being iterated
                name, image = db.session.query(Recipe.name, RecipePicture.filename).join(RecipePicture).filter(Recipe.id == recipe_id).all()[0]

                # Since it is a dictionary, identical names will overwrite. Add a space to indicate 'repeated'
                while name in current_menu:
                    name = name + ' '
                
                current_menu[name] = image
                    
            # Add current menu to full list of menus
            menus.append(current_menu)
        
        return render_template('menus.html', menus = menus, week = week)

    # If user not authenticated:

    return render_template('menus.html', menus = user_menus, week = week)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/new_recipe', methods=['GET', 'POST'])
def new_recipe():
    if 'recipes' not in session:
        session['recipes'] = []

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
                    continue
                # Split in maximum 2 parts (quantity and name)
                try:
                    float(ingredient[0])
                    quantity, name = ingredient.split(' ', 1)
                except:
                    quantity = 1
                    name = ingredient

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

            return redirect(url_for('show_recipes'))
        else:
            # Get recipe name
            recipe_name = data['recipe'];

            # Create dictionary for this recipe
            recipe = {}
            recipe['name'] = recipe_name

            # Save ingredients in recipe dictionary
            for ingredient in data.values():
                # Pass recipe because it is not an ingredient
                if ingredient == recipe_name:
                    continue
                # Split in maximum 2 parts (quantity and name)
                try:
                    float(ingredient[0])
                    quantity, name = ingredient.split(' ', 1)
                except:
                    quantity = ''
                    name = ingredient
                recipe[name] = quantity
            
            # Save recipe to session
            session['recipes'].append(recipe)

            flash ('Recipe saved!', 'no-margin alert alert-success')
            return redirect(url_for('show_recipes'))
    else:
        # print(session['recipes'], file=stderr)
        return render_template('new_recipe.html')

@app.route('/recipes')
def show_recipes():
    if current_user.is_authenticated:
        # Get current user id
        user_id = current_user.get_id()

        # Get all recipes for current user
        recipes = db.session.query(Recipe.name).filter(Recipe.user_id==user_id).all()

        # Create dictionary to hold all ingredients for each recipe
        full_recipes = {}
        recipe_images = []
        # Since query returns a named tuple, unpack tuple in for loop to use recipe name directly
        for recipe, in recipes:
            full_recipes[recipe] = db.session.query(Ingredient.quantity, Ingredient.name).filter(Ingredient.recipe_id.in_(db.session.query(Recipe.id).filter(Recipe.name==recipe))).all()[0]

             # Get image for recipe
            recipe_images.append(db.session.query(RecipePicture.filename).filter(RecipePicture.recipe_id.in_(db.session.query(Recipe.id).filter(Recipe.name==recipe).filter(Recipe.user_id==user_id))).all()[0])

        return render_template('recipes.html', recipes=full_recipes, recipe_images = recipe_images)
    else:
        if 'recipes' not in session:
            session['recipes'] = []
        recipes = session['recipes']
        # print(recipes, file=stderr)
        return render_template('recipes.html', recipes = recipes)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def create_menu():
    if current_user.is_authenticated:
        # Get user id
        user_id = current_user.get_id()

        # Get ids in tuple form
        recipe_tuples = db.session.query(Recipe.id).filter(Recipe.user_id==user_id).all()

        # Get id for each tuple
        recipe_ids = [tupl[0] for tupl in recipe_tuples]

        # Create a list of 7 recipes for a 1 week menu
        menu_list = []

        # List to keep track of which position of recipe_ids have been used.
        # This will prevent duplicated recipes when possible
        used_positions = []
        ids_quantity = len(recipe_ids)

        while len(menu_list) < 7:
            # If there are less than 7 recipes, some ids will be duplicated.
            # Clear used position when that happens, to allow a second round of selection
            
            if len(used_positions) == ids_quantity:
                used_positions.clear()

            # Get random position for recipe_ids
            random_position = randint(0, ids_quantity - 1)
            
            # If that id has been taken, select another
            while random_position in used_positions:
                random_position = randint(0, ids_quantity - 1)
            
            # Add id to menu
            menu_list.append(recipe_ids[random_position])
            used_positions.append(random_position)

        # Create menu object
        menu = Menu(
            recipe1_id = menu_list[0],
            recipe2_id = menu_list[1],
            recipe3_id = menu_list[2],
            recipe4_id = menu_list[3],
            recipe5_id = menu_list[4],
            recipe6_id = menu_list[5],
            recipe7_id = menu_list[6]
        )
        return menu
    
    # If user not authenticated
    # Make sure that there are at least 7 recipes, and repeat if needed
    if 'recipes' not in session:
        session['recipes'] = []
        flash('You don\'t have any recipes! Create here your first one.', 'no-margin alert alert-danger')
        return redirect(url_for('new_recipe'))

    recipes = session['recipes']
    
    while len(recipes) < 7:
        # Repeat recipes in random order until there is a total of 7 recipes
        recipes.append(recipes[randint(0, len(recipes) - 1)])

    # Randomize recipes to create a random menu
    shuffle(recipes)

    # Add menu to session
    menu = [
        recipes[0]['name'],
        recipes[1]['name'],
        recipes[2]['name'],
        recipes[3]['name'],
        recipes[4]['name'],
        recipes[5]['name'],
        recipes[6]['name']
    ]
    session['menus'].append(menu)
    print(menu, file=stderr)




def get_user_menus():
    if (current_user.is_authenticated):
        menus = db.session.query(
            Menu.id,
            Menu.recipe1_id,
            Menu.recipe2_id,
            Menu.recipe3_id,
            Menu.recipe4_id,
            Menu.recipe5_id,
            Menu.recipe6_id,
            Menu.recipe7_id
        ).filter(Menu.user_id == current_user.id).all()
        return menus

    if 'menus' not in session:
        session['menus'] = []
    
    return session['menus']



def delete_menu(menu_id):
    if current_user.is_authenticated:
        menu = Menu.query.filter(Menu.id == menu_id)
        menu.delete()
        db.session.commit()
    else:
        session['menus'].pop(int(menu_id))
