from flask import render_template, flash, redirect
from app import app
from .forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Miguel'} # fake user
    posts = [  # fake array of posts
    	{ 
    		'author': {'nickname': 'John'}, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	'''
		The validate_on_submit method does all the form processing work. If you call it when the form is being 
		presented to the user (i.e. before the user got a chance to enter data on it) then it will return 
		False, so in that case you know that you have to render the template.
	'''
	if form.validate_on_submit():
		flash('Login requested for OpenID="%s", remember_me=%s' % (form.openid.data, str(form.remember_me.data)))
		return redirect('/index')
	return render_template('login.html', title='Sign In', form=form, providers=app.config['OPENID_PROVIDERS'])
