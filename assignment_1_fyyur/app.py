# ---------------------------------------------------------------------------- #
# Imports
# ---------------------------------------------------------------------------- #

import json
from typing import List

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, \
    url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

# ---------------------------------------------------------------------------- #
# App Config.
# ---------------------------------------------------------------------------- #

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

# ---------------------------------------------------------------------------- #
# Filters.
# ---------------------------------------------------------------------------- #


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


def count_upcomming_show(shows: List[Show]) -> int:
    return len([show for show in shows if show.start_time > datetime.now()])


app.jinja_env.filters['datetime'] = format_datetime


# ---------------------------------------------------------------------------- #
# Controllers.
# ---------------------------------------------------------------------------- #


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # DONE: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.all()
    locals = Venue.query.distinct(Venue.city, Venue.state).all()
    data = []
    for local in locals:
        data.append({
            'city': local.city,
            'state': local.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
                'num_upcomming_shows': count_upcomming_show(venue.shows)
            } for venue in venues if venue.city == local.city and
                                     venue.state == local.state]
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    count = 0
    data = []
    search_str = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike('%' + search_str + '%')).all()

    response = {
        'count': len(venues),
        'data': []
    }

    for venue in venues:
        response['data'].append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': count_upcomming_show(venue.shows)
        })

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get_or_404(venue_id)
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        show_data = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.isoformat()
        }
        if show.start_time >= datetime.now():
            upcoming_shows.append(show_data)
        else:
            past_shows.append(show_data)

    data = vars(venue)
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    try:
        # DONE: insert form data as a new Venue record in the db, instead
        # genres = ''
        # for genre in request.form.getlist('genres'):
        #     genres += genre + ','
        # seeking_talent = True if request.form.get(
        #     'seeking_talent') == 'y' else False

        # DONE: modify data to be the data object returned from db insertion
        venue = Venue(name=form.name.data, city=form.city.data,
                      state=form.state.data, address=form.address.data,
                      phone=form.phone.data, genres=form.genres.data,
                      facebook_link=form.facebook_link.data,
                      image_link=form.image_link.data,
                      website_link=form.website_link.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data)
        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as ex:
        db.session.rollback()
        # DONE: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        print(ex.__str__())
        flash('An error occurred. Venue could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue was successfully deleted!')
    except Exception as ex:
        print(ex)
        db.session.rollback()
        flash('Deleting venue error!')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = [{
        'id': artist.id,
        'name': artist.name
    } for artist in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    count = 0
    data = []
    search_str = request.form.get('search_term')
    artists = Artist.query.all()
    for artist in artists:
        if artist.name.lower().find(search_str) != -1:
            count += 1
            data.append({
                'id': artist.id,
                'name': artist.name,
                'num_upcoming_shows': len(artist.shows)
            })
    response = {
        'count': count,
        'data': data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # DONE: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get_or_404(artist_id)
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        show_data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.isoformat()
        }
        if show.start_time >= datetime.now():
            upcoming_shows.append(show_data)
        else:
            past_shows.append(show_data)

    data = vars(artist)
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # DONE: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(**artist.__dict__)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    try:
        artist = Venue.query.get_or_404(artist_id)
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website_link = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.commit()
    except Exception as ex:
        print(ex)
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # form = VenueForm()
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # DONE: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(**venue.__dict__)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    try:
        venue = Venue.query.get_or_404(venue_id)
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website_link = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
    except Exception as ex:
        print(ex)
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form = ArtistForm(request.form)
    try:
        # DONE: insert form data as a new Venue record in the db, instead
        # DONE: modify data to be the data object returned from db insertion
        artist = Artist(name=form.name.data, city=form.city.data,
                        state=form.state.data, phone=form.phone.data,
                        genres=form.genres.data,
                        facebook_link=form.facebook_link.data,
                        image_link=form.image_link.data,
                        website_link=form.website_link.data,
                        seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data)
        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as ex:
        db.session.rollback()
        # DONE: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        print(ex.__str__())
        flash('An error occurred. Artist could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get_or_404(artist_id)
        db.session.delete(artist)
        db.session.commit()
        flash('Artist was successfully deleted!')
    except Exception as ex:
        print(ex)
        db.session.rollback()
        flash('Deleting artist error!')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.

    shows = Show.query.all()
    data = [{
        'venue_id': show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.isoformat()
    } for show in shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    try:
        # DONE: insert form data as a new Show record in the db, instead
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as ex:
        db.session.rollback()
        # DONE: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ---------------------------------------------------------------------------- #
# Launch.
# ---------------------------------------------------------------------------- #

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
