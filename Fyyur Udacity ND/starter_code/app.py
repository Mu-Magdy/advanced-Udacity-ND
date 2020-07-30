#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *


# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en_US')


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
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.all()
    data = []
    places = set()
    for venue in venues:
        places.add((venue.city, venue.state))

    for place in places:
        data.append({
            "city": place[0],
            "state": place[1],
            "venues": []
        })

    for venue in venues:
        num_upcoming_shows = 0
        shows = Show.query.filter_by(venue_id=venue.id).all()
        cur_date = datetime.now()
        for show in shows:
            if show.start_time >= cur_date:
                num_upcoming_shows += 1
        for place in data:
            if venue.state == place['state'] and venue.city == place['city']:
                place['venues'].append({
                    'id': venue.id,
                    'name': venue.name,
                    "num_upcoming_shows": num_upcoming_shows
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    venues = db.session.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%')).all()
    data = []
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,

        })

    response = {
        "count": len(venues),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    upcoming_shows = []
    past_shows = []
    cur_time = datetime.now()
    for show in shows:
        data = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time >= cur_time:
            upcoming_shows.append(data)
        else:
            past_shows.append(data)
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()

    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    error = False
    try:
        # TODO checked: modify data to be the data object returned from db insertion
        new_venue = Venue(name=request.form.get('name'),
                          city=request.form.get('city'),
                          state=request.form.get('state'),
                          address=request.form.get('address'),
                          phone=request.form.get('phone'),
                          image_link=request.form.get('image_link'),
                          genres=request.form.getlist('genres'),
                          facebook_link=request.form.get('facebook_link'),
                          seeking_description=request.form.get(
            'seeking_description'),
            website=request.form.get('website'),
            seeking_talent=request.form.get('seeking_talent'))
        if request.form.get('seeking_talent') == 'y':
            new_venue.seeking_talent = True

        db.session.add(new_venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()

    finally:
        db.session.close()
        if error:
         # TODO checked: on unsuccessful db insert, flash an error instead.# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            flash('An error occurred. Venue ' +
                  request.form.get('name') + ' could not be listed.')
        elif not error:
         # on successful db insert, flash success
            flash('Venue ' + request.form.get('name') +
                  ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()

    except:
        error = True
        db.session.rollback()

    finally:

        db.session.close()
    if error:
        flash('an error occured and Venue ' + venue.name + ' has a show')
    if not error:
        flash('Venue ' + venue.name + ' was deleted')
    return render_template('pages/home.html')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append(artist)

    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '')
    artists = db.session.query(Artist).filter(
        Artist.name.ilike(f'%{search_term}%')).all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name

        })

    response = {
        "count": len(artists),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()

    for show in shows:
        data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > current_time:
            upcoming_shows.append(data)
        else:
            past_shows.append(data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "website": artist.website,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm()
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website.data
        artist.image_link = form.image_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.commit()
        flash(f'Artist {artist.name} edited successfully')
    except:
        db.session.rollback()
        flash(f'Artist {artist.name} edit failed')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id, form=form))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # TODO: populate form with values from venue with ID <venue_id>

    venue = Venue.query.get(venue_id)
    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "facebook_link": venue.facebook_link,
        "website": venue.website,
        "image_link": venue.image_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
        flash(f'Venue {venue.name} edited successfully')
    except:
        db.session.rollback()
        flash(f'Venue {venue.name} edit failed')
    finally:
        db.session.close()

    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id, form=form))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    try:
        # TODO: modify data to be the data object returned from db insertion
        new_artist = Artist(name=request.form.get('name'),
                            city=request.form.get('city'),
                            state=request.form.get('state'),
                            phone=request.form.get('phone'),
                            image_link=request.form.get('image_link'),
                            genres=request.form.getlist('genres'),
                            facebook_link=request.form.get('facebook_link'),
                            seeking_description=request.form.get(
            'seeking_description'),
            website=request.form.get('website'),
            seeking_venue=request.form.get('seeking_venue'))
        if request.form.get('seeking_venue') == 'y':
            new_artist.seeking_venue = True
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:

        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')

    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()

    finally:

        db.session.close()
    if error:
        flash('an error occured and Venue ' + artist.name + ' has a show')
    if not error:
        flash('Venue ' + artist.name + ' was deleted')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time":  format_datetime(str(show.start_time)),
        })
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:

        new_show = Show(artist_id=request.form.get('artist_id'), venue_id=request.form.get(
            'venue_id'), start_time=request.form.get('start_time'))
        # on successful db insert, flash success

        db.session.add(new_show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.

    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    elif not error:
        flash('Show was successfully listed!')
    return render_template('pages/home.html')


@ app.route('/shows/search', methods=['POST'])
# def search_shows():
#     # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
#     # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
#     # search for "band" should return "The Wild Sax Band".
#     search_term = request.form.get('search_term', '')
#     show = Show.query.all()
#     artist = Artist.query.all()
#     shows = db.session.query(Show).filter(
#         Artist.name.ilike(f'%{search_term}%')).all()
#     data = []
#     for show in shows:
#         data.append({
#             "id": show.artist_id,
#         })
#     response = {
#         "count": len(shows),
#         "data": data
#     }
#     return render_template('pages/search_shows.html', results=response, search_term=request.form.get('search_term', ''), artist=artist)
# @app.route('/shows/<show_id>', methods=['DELETE'])
# def delete_show(show_id):
#     # TODO: Complete this endpoint for taking a venue_id, and using
#     # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
#     error = False
#     try:
#         show = Show.query.get(show_id)
#         db.session.delete(show)
#         db.session.commit()
#     except:
#         error = True
#         db.session.rollback()
#     finally:
#         db.session.close()
#     if error:
#         flash('an error occured and the show was not deleted')
#     if not error:
#         flash('Show was deleted')
#     return render_template('pages/home.html')
@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
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
