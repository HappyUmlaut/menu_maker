from app import app
from app import db
from flask_login import current_user, login_user, logout_user
from app.models import User
from flask import redirect, flash, url_for, render_template
from app.forms import LoginForm, RegistrationForm

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

@app.route('/new_recipe')
def new_recipe():
    return render_template('new_recipe.html')

@app.route('/recipes')
def show_recipes():
    return render_template('recipes.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))