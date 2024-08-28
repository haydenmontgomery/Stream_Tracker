import os

import requests
import aiohttp
import asyncio
import json
import ast
from operator import itemgetter
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, Movie, Subscription, User_Likes_Movie, Service


CURR_USER_KEY = "curr_user"
HEADERS = {
                "accept": "application/json",
                "Authorization": os.environ.get('TMDB_API_KEY')
            }
SUBSCRIPTIONS = ['Amazon Prime Video', 'Netflix', 'Disney Plus', 'HBO Max', 'Hulu', 'Peacock', 'Paramount Plus', 'Starz', 'Showtime', 'Apple TV Plus']

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

    """ app.app_context().push()
    connect_db(app) """


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
                flash('Changes updated', "info")
                return redirect('/')
            
            flash('Invalid Credentials', "danger")
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

    @app.route('/search', methods=['GET', 'POST'])
    def search_movies():
        """Search page. Takes arguments from searchbar, uses omdb api to get movies from search term."""
           

        """Make sure we query only if nothing is in our session just to be sure"""
        search = request.args.get('q')

        url = f"https://api.themoviedb.org/3/search/movie?query={search}&include_adult=false&language=en-US&page=1"
        search_response = requests.get(url, headers=HEADERS)

        """This section is making it easier for jinja to use.
        Jsons the values, maps the results then sorts them by popularity so the most popular movie in the search is displayed first.
        """
        movie_values = search_response.json().get('results')
        movie_newlist = sorted(movie_values, key=itemgetter('popularity'), reverse=True)
        """ for result in results:
            print(result.get('id')) """

        updated_movies_list = asyncio.run(main_get(movie_newlist))
        """Use session here so we don't keep making requests to the api"""
        session['api_data'] = updated_movies_list
        session.modified = True

        return render_template('movie_search.html', results=session['api_data'])

    async def get_providers(session, movie):
        """Async function so we can loop through each movie and call the providers api"""
        movie_id = movie['id']
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"

        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                result = await response.json()
                another = result.get('results')
                us = another.get('US')
                if us == None:
                    movie['flatrate'] = None
                    return movie
                flatrate = us.get('flatrate')
                movie['flatrate'] = flatrate
                return movie
            else:
                print(f"Failed to get data for movie ID {movie_id}: {response.status}")
                movie['flatrate'] = flatrate
                return movie
        
    async def main_get(movies):
        """Main async function for calling the providers api"""
        async with aiohttp.ClientSession() as session:
            tasks = [get_providers(session, movie) for movie in movies]
            updated_movies = await asyncio.gather(*tasks)
            return updated_movies
    
    @app.route('/movies/like', methods=['POST'])
    def watchlist_button():
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        

        # This is called when a user clicks to add a movie to watchlist
        movie_info_str = request.form.get('add_watchlist') # gets the selected movie
        if movie_info_str:
            try:
                dict_obj = ast.literal_eval(movie_info_str) # converts to dictionary
                new_id = int(dict_obj.get('id'))
                movie = Movie.query.filter_by(movie_id=new_id).first()
                if not movie:
                    movie = Movie(movie_id=int(dict_obj.get('id')), name=dict_obj.get('title'), description=dict_obj.get('overview'), image_url=dict_obj.get('poster_path'), year=dict_obj.get('release_date'))
                    db.session.add(movie)
                    db.session.commit()
                likes = User_Likes_Movie.query.filter_by(user_liking_id=g.user.id, liked_movie_id=movie.id).first()
                if not likes:
                    likes = User_Likes_Movie(user_liking_id=g.user.id, liked_movie_id=movie.id)
                    db.session.add(likes)
                    db.session.commit()
                services = []
                flatrate = dict_obj.get('flatrate')

                for service in flatrate:
                    if service.get('provider_name') in SUBSCRIPTIONS:
                        services.append(service.get('provider_name'))

                for service in services:
                    db_service = Service.query.filter_by(name=service).first()
                    subscription = Subscription.query.filter_by(movie_id=movie.id, service_id=db_service.id).first()
                    if not subscription:
                        subscription = Subscription(movie_id=movie.id, service_id=db_service.id)
                        db.session.add(subscription)
                        db.session.commit()
                title = dict_obj.get('title')
                results = {'message': f'Added {title} to watchlist!'}
            except ValueError as e:
                print("Error converting string to dictionary", e)
        return jsonify(results)
    
    @app.route('/watchlist')
    def watchlist():
        """Displays user's list of movies to watch"""
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        
        user_likes = User_Likes_Movie.query.filter_by(user_liking_id=g.user.id).all()
        movie_dict = []

        for like in user_likes:
            movie = Movie.query.get(like.liked_movie_id)
            subscription_list = []
            subscription_query = Subscription.query.filter_by(movie_id=movie.id).all()
            for subscription in subscription_query:
                service = Service.query.get(subscription.service_id)
                if user_subscription_switch_case(service):
                    subscription_list.append(service.image_url)
            dict_subscriptions = {movie.id: [movie, subscription_list]}
            movie_dict.append(dict_subscriptions)

        return render_template('watchlist.html', movie_dict=movie_dict)

    def user_subscription_switch_case(service):
        if g.user.netflix and service.id == 1:
            return True
        elif g.user.prime_video and service.id == 2:
            return True
        elif g.user.disney_plus and service.id == 3:
            return True
        elif g.user.hbo_max and service.id == 4:
            return True
        elif g.user.hulu and service.id == 5:
            return True
        elif g.user.peacock and service.id == 6:
            return True
        elif g.user.paramount_plus and service.id == 7:
            return True
        elif g.user.starz and service.id == 8:
            return True
        elif g.user.showtime and service.id == 9:
            return True
        elif g.user.apple_tv  and service.id == 9:
            return True
        else:
            return False



    @app.route('/movies/<int:id>/remove_watchlist', methods=['POST'])
    def remove_watchlist(id):
        """Removes the movie from the user's watchlist"""
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        likes = User_Likes_Movie.query.filter_by(user_liking_id=g.user.id, liked_movie_id=id).first()
        if likes.user_liking_id != g.user.id:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        db.session.delete(likes)
        db.session.commit()
        flash("Removed from watchlist", "info")
        return redirect(request.referrer)

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