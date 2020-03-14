# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
# Import the database object from the main app module
from app import db

# Import module forms
from app.main_page_module.forms import LoginForm, RegisterForm

# Import module models (i.e. User)
from app.main_page_module.models import User


# Define the blueprint: 'auth', set its url prefix: app.url/auth
main_page_module = Blueprint('main_page_module', __name__, url_prefix='/')


# Set the route and accepted methods
@main_page_module.route('/', methods=['GET', 'POST'])
def index():

    return render_template("main_page_module/index.html")

# Set the route and accepted methods
@main_page_module.route('/login/', methods=['GET', 'POST'])
def login():

    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username_or_email.data).first()
        if not user:
            user = User.query.filter_by(email=form.username_or_email.data).first()

        if user and user.check_password(form.password.data):

            session['user_id'] = user.id

            flash('Welcome %s' % user.name, 'success')
            
            return redirect(url_for('main_page_module.index'))

        flash('Wrong email or password', 'error')
    
    try:
        if(session['user_id']):
            return redirect(url_for("main_page_module.index"))
    
    except:
        return render_template("main_page_module/auth/login.html", form=form)
        

@main_page_module.route('/logout/')
def logout():
    session.pop("user_id", None)
    
    flash('You have been logged out. Have a nice day!', 'success')

    return redirect(url_for("main_page_module.login"))

# Set the route and accepted methods
@main_page_module.route('/register/', methods=['GET', 'POST'])
def register():
    #insert check, if the user is already logged in
    form = RegisterForm(request.form)
    print(form.username.data)
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password = form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        
        return redirect(url_for('main_page_module.login'))
    return render_template('main_page_module/auth/register.html', title='Register', form=form)