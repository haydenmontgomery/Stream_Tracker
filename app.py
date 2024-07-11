import os

import requests
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, Movie, Subscription

CURR_USER_KEY = "curr_user"
OMDB_URL = "https://omdb-api4.p.rapidapi.com/"
def create_app(database_name, testing=False):

    app = Flask(__name__)

    # Get DB_URI from environ variable (useful for production/testing) or,
    # if not set there, use development local db.
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL', f'postgresql:///{database_name}'))

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
    toolbar = DebugToolbarExtension(app)

    app.app_context().push()
    connect_db(app)


    ##############################################################################
    # User signup/login/logout


    @app.before_request
    def add_user_to_g():
        """If we're logged in, add curr user to Flask global."""

        if CURR_USER_KEY in session:
            g.user = User.query.get(session[CURR_USER_KEY])

        else:
            g.user = None


    def do_login(user):
        """Log in user."""

        session[CURR_USER_KEY] = user.id


    def do_logout():
        """Logout user."""

        if CURR_USER_KEY in session:
            del session[CURR_USER_KEY]


    @app.route('/signup', methods=["GET", "POST"])
    def signup():
        """Handle user signup.

        Create new user and add to DB. Redirect to home page.

        If form not valid, present form.

        If the there already is a user with that username: flash message
        and re-present form.
        """

        form = UserAddForm()

        if form.validate_on_submit():
            try:
                user = User.signup(
                    username=form.username.data,
                    password=form.password.data,
                    email=form.email.data,
                    image_url=form.image_url.data or User.image_url.default.arg,
                )
                db.session.commit()

            except IntegrityError:
                flash("Username already taken", 'danger')
                return render_template('users/signup.html', form=form)

            do_login(user)

            return redirect("/")

        else:
            return render_template('users/signup.html', form=form)


    @app.route('/login', methods=["GET", "POST"])
    def login():
        """Handle user login."""

        form = LoginForm()

        if form.validate_on_submit():
            user = User.authenticate(form.username.data,
                                     form.password.data)

            if user:
                do_login(user)
                flash(f"Hello, {user.username}!", "success")
                return redirect("/")

            flash("Invalid credentials.", 'danger')

        return render_template('users/login.html', form=form)


    @app.route('/logout')
    def logout():
        """Handle logout of user."""
        
        # IMPLEMENT THIS
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect('/')
        do_logout()
        flash("Come back soon!", "info")
        return redirect('/')

    ##############################################################################
    # General user routes:

    """     @app.route('/users/follow/<int:follow_id>', methods=['POST'])
    def add_follow(follow_id):
        #Add a follow for the currently-logged-in user.

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        followed_user = User.query.get_or_404(follow_id)
        g.user.following.append(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following") """

    @app.route('/users/profile', methods=["GET", "POST"])
    def profile():
        """Update profile for current user."""

        # IMPLEMENT THIS
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        
        form = UserEditForm(username=g.user.username, email=g.user.email, image_url=g.user.image_url, netflix = g.user.netflix, prime_video = g.user.prime_video, disney_plus = g.user.disney_plus, hbo_max = g.user.hbo_max, hulu = g.user.hulu, peacock = g.user.peacock, paramount_plus = g.user.paramount_plus, starz = g.user.starz, showtime = g.user.showtime, apple_tv = g.user.apple_tv)


        if form.validate_on_submit():
            user = User.authenticate(g.user.username,
                                     form.password.data)
            
            if user:
                user.username = form.username.data
                user.email = form.email.data
                user.image_url = form.image_url.data
                user.netflix = form.netflix.data
                user.prime_video = form.prime_video.data
                user.disney_plus = form.disney_plus.data
                user.hbo_max = form.hbo_max.data
                user.hulu = form.hulu.data
                user.peacock = form.peacock.data
                user.paramount_plus = form.paramount_plus.data
                user.starz = form.starz.data
                user.showtime = form.showtime.data
                user.apple_tv = form.apple_tv.data
                db.session.add(user)
                db.session.commit()
                flash(f'Changes updated', "info")
                return redirect('/')
            
            flash(f'Invalid Credentials', "danger")
            return redirect('/')
        return render_template('users/edit.html', form=form)




    @app.route('/users/delete', methods=["POST"])
    def delete_user():
        """Delete user."""

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        do_logout()

        db.session.delete(g.user)
        db.session.commit()

        return redirect("/signup")


    ##############################################################################
    # Movie routes?

    @app.route('/search')
    def search_movies():
        """Search page. Takes arguments from searchbar, uses omdb api to get movies from search term."""

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        search = request.args.get('q')

        if not search:
            return redirect('/')
        else:
            querystring = {"s": search}
            headers = {
                "x-rapidapi-key": os.environ['RAPID_API_KEY'] ,
	            "x-rapidapi-host": "omdb-api4.p.rapidapi.com",
	            "Content-Type": "application/json"
            }
            response = requests.get(OMDB_URL, headers=headers, params=querystring)

        return render_template('movie_search.html', response=response)

    ##############################################################################
    # Homepage and error pages


    @app.route('/')
    def homepage():
        """Show homepage"""
        return render_template('home.html')
    
    @app.route('/about')
    def about():
        """The about page"""
        return render_template('about.html')
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.after_request
    def add_header(req):
        """Add non-caching headers on every request."""

        req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        req.headers["Pragma"] = "no-cache"
        req.headers["Expires"] = "0"
        req.headers['Cache-Control'] = 'public, max-age=0'
        return req
    return app

if __name__=='__main__':
    app = create_app('stream_tracker_db')
    #connect_db(app)
    app.run(debug=True)