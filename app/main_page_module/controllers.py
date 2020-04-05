# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify
# Import the database object from the main app module
from app import db

# Import module forms
from app.main_page_module.forms import LoginForm, RegisterForm, EditUserForm

# Import module models (i.e. User)
from app.main_page_module.models import User
#import os
import re
import os


# Define the blueprint: 'auth', set its url prefix: app.url/auth
main_page_module = Blueprint('main_page_module', __name__, url_prefix='/')

#login check
def check_login():
    if "user_id" not in session:
        return True
        
    
# Set the route and accepted methods
@main_page_module.route('/', methods=['GET', 'POST'])
def index():
    if check_login(): return redirect(url_for("main_page_module.login"))  

    return render_template("main_page_module/index.html")
        
@main_page_module.route('/admin/all_users/')
def all_users():
    if check_login(): return redirect(url_for("main_page_module.login"))  
    
    users = User.query.all()
   
    return render_template("main_page_module/admin/all_users.html", users=users)


@main_page_module.route('/admin/view_user/<user_id>')
def view_user(user_id):
    if check_login(): return redirect(url_for("main_page_module.login"))  
    
    user = User.query.filter_by(id=user_id).first()
   
    if not user:
        flash('User does not exist.', 'error')
        
        return redirect(url_for("main_page_module.all_users"))     
    
    form = EditUserForm()
    form.process(obj=user)
    
   
    return render_template("main_page_module/admin/view_user.html", form=form, user=user)

@main_page_module.route('/admin/modify_user/', methods=['POST'])
def modify_user():
    if check_login(): return redirect(url_for("main_page_module.login"))  
    
    form = EditUserForm(request.form)
    
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.id.data).first()
        
        if not user:
            flash('User does not exist.', 'error')
        
            return redirect(url_for("main_page_module.all_users")) 
        
        else:
            user.name =  form.name.data
            user.email =  form.email.data
            if form.password.data != "":
                user.set_password(form.password.data)
    
            db.session.commit()   
        
        flash('User successfully Eddited!', 'success')
        
        return redirect(url_for("main_page_module.view_user", user_id=form.id.data, form=form))
    
    flash('Invalid data.', 'error')

    return redirect(url_for("main_page_module.all_users"))     
    

@main_page_module.route('/admin/delete/', methods=['POST'])
def delete_user():
    if check_login(): return redirect(url_for("main_page_module.login"))  
    
    user_id = request.form["id"]
    
    user = User.query.filter_by(id=user_id).first()
   
    if not user:
        flash('User does not exist.', 'error')
        
        return redirect(url_for("main_page_module.all_users")) 
    
    else:
        db.session.delete(user)
        db.session.commit()        
        
        flash(f'User {user.name} - {user.username} successfully deleted.', 'success')
        
        return redirect(url_for("main_page_module.all_users")) 
    

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
            
            #set permanent login, if selected
            if form.remember.data == True:
                session.permanent = True

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
    session.permanent = False
    
    flash('You have been logged out. Have a nice day!', 'success')

    return redirect(url_for("main_page_module.login"))

# Set the route and accepted methods
@main_page_module.route('/register/', methods=['GET', 'POST'])
def register():
    #insert check, if the user is already logged in
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password = form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        
        return redirect(url_for('main_page_module.login'))
    return render_template('main_page_module/auth/register.html', title='Register', form=form)