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
import sys

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
    error=False
    try:
        name = request.form['name']
        VenueForm().validate_phone(VenueForm, VenueForm().phone)
        VenueForm().validate_genres(VenueForm, VenueForm().genres)
        city = request.form['city']
        state= request.form['state']
        address= request.form['address']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        seeking_talent_exist = request.form.get('seeking_talent', None)
        if seeking_talent_exist is None:
          seeking_talent = False
        else:
          seeking_talent = True
        seeking_description = request.form['seeking_description'] 
        image_link = request.form['image_link']
        website = request.form['website']
        facebook_link = request.form['facebook_link']
        venue = Venue(name=name, city=city, state=state, phone=phone, address=address, genres=genres, image_link=image_link,
        facebook_link=facebook_link, seeking_description=seeking_description, seeking_talent=seeking_talent, website=website )
        db.session.add(venue)
        db.session.commit()
    except Exception as e:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + name + ' could not be listed due to ' + str(e))
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + name + ' was successfully listed!')
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
    try:
        form = ArtistForm()
        artistList = Artist.query.filter_by(id=artist_id).one_or_none()
        if artistList is None:
            abort(404)
        artist = {
            "id": artistList.id,
            "name": artistList.name
        }
        form.name.data = artistList.name
        form.genres.data = artistList.genres
        form.city.data = artistList.city
        form.state.data = artistList.state
        form.phone.data = artistList.phone
        form.website.data = artistList.website
        form.facebook_link.data = artistList.facebook_link
        form.seeking_venue.data = artistList.seeking_venue
        form.seeking_description.data = artistList.seeking_description
        form.image_link.data = artistList.image_link
    except:
        abort(404)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error=False
    try:
        ArtistForm().validate_phone(ArtistForm, ArtistForm().phone)
        ArtistForm().validate_genres(ArtistForm, ArtistForm().genres)
        seeking_venue_exist = request.form.get('seeking_venue', None)
        if seeking_venue_exist is None:
          seeking_venue = False
        else:
          seeking_venue = True
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.seeking_venue = seeking_venue
        artist.seeking_description = request.form['seeking_description'] 
        artist.image_link = request.form['image_link']
        artist.website = request.form['website']
        artist.facebook_link = request.form['facebook_link']
        db.session.commit()
    except Exception as e:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited due to ' + str(e))
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        form = VenueForm()
        venueList = Venue.query.filter_by(id=venue_id).one_or_none()
        if venueList is None:
            abort(404)
        venue = {
            "id": venueList.id,
            "name": venueList.name
        }
        form.name.data = venueList.name
        form.genres.data = venueList.genres
        form.address.data = venueList.address
        form.city.data = venueList.city
        form.state.data = venueList.state
        form.phone.data = venueList.phone
        form.website.data = venueList.website
        form.facebook_link.data = venueList.facebook_link
        form.seeking_description.data = venueList.seeking_description
        form.seeking_talent.data = venueList.seeking_talent
        form.image_link.data = venueList.image_link
    except:
        abort(404)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error=False
    try:
        VenueForm().validate_phone(VenueForm, VenueForm().phone)
        VenueForm().validate_genres(VenueForm, VenueForm().genres)
        seeking_talent_exist = request.form.get('seeking_talent', None)
        if seeking_talent_exist is None:
          seeking_talent = False
        else:
          seeking_talent = True
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.address = request.form['address']
        venue.state = request.form['state']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.seeking_talent = seeking_talent
        venue.seeking_description = request.form['seeking_description'] 
        venue.image_link = request.form['image_link']
        venue.website = request.form['website']
        venue.facebook_link = request.form['facebook_link']
        db.session.commit()
    except Exception as e:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited due to ' + str(e))
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error=False
    try:
        name = request.form['name']
        ArtistForm().validate_phone(ArtistForm, ArtistForm().phone)
        ArtistForm().validate_genres(ArtistForm, ArtistForm().genres)
        city = request.form['city']
        state= request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        seeking_venue_exist = request.form.get('seeking_venue', None)
        if seeking_venue_exist is None:
          seeking_venue = False
        else:
          seeking_venue = True
        seeking_description = request.form['seeking_description'] 
        image_link = request.form['image_link']
        website = request.form['website']
        facebook_link = request.form['facebook_link']
        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link,
        facebook_link=facebook_link, seeking_description=seeking_description, seeking_venue=seeking_venue, website=website )
        db.session.add(artist)
        db.session.commit()
    except Exception as e:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + name + ' could not be listed due to ' + str(e))
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + name + ' was successfully listed!')
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
    error=False
    try:
        artist = Artist.query.filter_by(id = request.form['artist_id']).one_or_none()
        if artist is None:
          raise 
        venue = Venue.query.filter_by(id = request.form['venue_id']).one_or_none()
        if artist is None:
          raise 
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time= request.form['start_time']
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed. Check if the provided Venue ID and Artist ID is valid')
    finally:
        db.session.close()
    if not error:
        flash('Show was successfully listed!')
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
