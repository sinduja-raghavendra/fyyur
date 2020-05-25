#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ragu@localhost:5432/fyyurapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'<{self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    cities = Venue.query.distinct('city').all()
    data = []
    for city in cities:
        values = {}
        values['city'] = city.city
        values['state'] = city.state
        venueLists = Venue.query.filter_by(city=city.city).order_by('id').all()
        venues = []
        for show in venueLists:
            num_upcoming_shows = 0
            shows = Show.query.filter_by(venue_id=show.id).all()
            for sh in shows:
              if (sh.start_time > datetime.today()):
                num_upcoming_shows += 1
            venueList = {}
            venueList['id'] = show.id
            venueList['name'] = show.name
            venueList['num_upcoming_shows'] = num_upcoming_shows
            venues.append(venueList.copy())
        values['venues'] = venues
        data.append(values.copy())
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_venue = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike('%'+search_venue+'%'))
    data = []
    for venue in venues:
      num_upcoming_shows = 0
      shows = Show.query.filter_by(venue_id=venue.id).all()
      for sh in shows:
        if (sh.start_time > datetime.today()):
          num_upcoming_shows += 1
      values = {}
      values['id'] = venue.id
      values['name'] = venue.name
      values['num_upcoming_shows'] = num_upcoming_shows
      data.append(values.copy())
    response = {
        "count": len(data)
    }
    response["data"] = data
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        showLists = Show.query.join(Venue).join(Artist).add_columns(Show.id.label('show_id'), Venue.id.label('venue_id'), Artist.id.label('artist_id'), Artist.name.label(
            'artist_name'), Artist.seeking_venue.label('artist_seeking_venue'), Artist.seeking_description.label('artist_seeking_description'), Artist.website.label('artist_website'), Artist.facebook_link.label('artist_facebook_link'), Artist.state.label('artist_state'), Artist.phone.label('artist_phone'), Artist.city.label('artist_city'), Artist.genres.label('artist_genres'), Artist.image_link.label('artist_image_link'), Show.start_time, Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link')).filter(Show.venue_id == venue_id).all()
        venuList = Venue.query.filter(Venue.id == venue_id).one_or_none()
        if venuList is None:
            abort(404)
        showList = []
        upcomingShowList = []
        if len(showLists) > 0:
            for show in showLists:
                if (show.start_time < datetime.today()):
                    past_shows = {}
                    past_shows['artist_id'] = show.artist_id
                    past_shows['artist_name'] = show.artist_name
                    past_shows['artist_image_link'] = show.artist_image_link
                    past_shows['start_time'] = show.start_time.strftime(
                        "%Y-%m-%dT%H:%M:%f")
                    showList.append(past_shows.copy())
                else:
                    upcoming_shows = {}
                    upcoming_shows['artist_id'] = show.artist_id
                    upcoming_shows['artist_name'] = show.artist_name
                    upcoming_shows['artist_image_link'] = show.artist_image_link
                    upcoming_shows['start_time'] = show.start_time.strftime(
                        "%Y-%m-%dT%H:%M:%f")
                    upcomingShowList.append(upcoming_shows.copy())
        data = {
            "id": venuList.id,
            "name": venuList.name,
            "genres": venuList.genres,
            "address": venuList.address,
            "city": venuList.city,
            "state": venuList.state,
            "phone": venuList.phone,
            "website": venuList.website,
            "facebook_link": venuList.facebook_link,
            "seeking_talent": venuList.seeking_talent,
            "seeking_description": venuList.seeking_description,
            "image_link": venuList.image_link,
            "past_shows_count": len(showList),
            "upcoming_shows_count": len(upcomingShowList),
        }
        data["past_shows"] = showList
        data["upcoming_shows"] = upcomingShowList
        return render_template('pages/show_venue.html', venue=data)
    except:
        abort(404)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.order_by('id').all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_artist = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike('%'+search_artist+'%'))
    data = []
    for artist in artists:
      num_upcoming_shows = 0
      shows = Show.query.filter_by(artist_id=artist.id).all()
      for sh in shows:
        if (sh.start_time > datetime.today()):
          num_upcoming_shows += 1
      values = {}
      values['id'] = artist.id
      values['name'] = artist.name
      values['num_upcoming_shows'] = num_upcoming_shows
      data.append(values.copy())
    response = {
        "count": len(data)
    }
    response["data"] = data
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    try:
        showLists = Show.query.join(Venue).join(Artist).add_columns(Show.id.label('show_id'), Venue.id.label('venue_id'), Artist.id.label(
            'artist_id'), Show.start_time, Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link')).filter(Show.artist_id == artist_id).all()
        artistList = Artist.query.filter(Artist.id == artist_id).one_or_none()
        if artistList is None:
            abort(404)
        showList = []
        upcomingShowList = []
        for show in showLists:
            if (show.start_time < datetime.today()):
                past_shows = {}
                past_shows['venue_id'] = show.venue_id
                past_shows['venue_name'] = show.venue_name
                past_shows['venue_image_link'] = show.venue_image_link
                past_shows['start_time'] = show.start_time.strftime(
                    "%Y-%m-%dT%H:%M:%f")
                showList.append(past_shows.copy())
            else:
                upcoming_shows = {}
                upcoming_shows['venue_id'] = show.venue_id
                upcoming_shows['venue_name'] = show.venue_name
                upcoming_shows['venue_image_link'] = show.venue_image_link
                upcoming_shows['start_time'] = show.start_time.strftime(
                    "%Y-%m-%dT%H:%M:%f")
                upcomingShowList.append(upcoming_shows.copy())
        data = {
            "id": artistList.id,
            "name": artistList.name,
            "genres": artistList.genres,
            "city": artistList.city,
            "state": artistList.state,
            "phone": artistList.phone,
            "website": artistList.website,
            "facebook_link": artistList.facebook_link,
            "seeking_venue": artistList.seeking_venue,
            "seeking_description": artistList.seeking_description,
            "image_link": artistList.image_link,
            "past_shows_count": len(showList),
            "upcoming_shows_count": len(upcomingShowList),
        }
        data["past_shows"] = showList
        data["upcoming_shows"] = upcomingShowList
        return render_template('pages/show_artist.html', artist=data)
    except:
        abort(404)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.join(Venue).join(Artist).add_columns(Show.id.label('show_id'), Venue.id.label('venue_id'), Artist.id.label(
        'artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time, Venue.name.label('venue_name')).all()
    data = []
    for show in shows:
        showList = {}
        showList['venue_id'] = show.venue_id
        showList['venue_name'] = show.venue_name
        showList['artist_id'] = show.artist_id
        showList['artist_name'] = show.artist_name
        showList['artist_image_link'] = show.artist_image_link
        showList['start_time'] = show.start_time.strftime("%Y-%m-%dT%H:%M:%f")
        data.append(showList.copy())
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
