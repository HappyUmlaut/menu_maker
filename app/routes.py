from app import app
from flask_login import current_user, login_user
from app.models import User
from flask import redirect, flash, url_for, render_template

@app.route('/')
def index():
    return render_template('base.html')
