import logging
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
import sys

from forms import *
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
from models import Venue, Artist, db, Show

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.all()
    areas = []
    response = []
    for venue in venues:
        city = venue.city
        state = venue.state
        if f'{city} {state}' not in areas:
            area = {
                "city": city,
                "state": state,
                "venues": Venue.query.filter_by(city=venue.city, state=venue.state)
            }
            response.append(area)
    return render_template('pages/venues.html', areas=response)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = f"%{request.form.get('search_term', '')}%"
    results = Venue.query.filter(Venue.name.ilike(search_term))

    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }

    response = {
        "count": len(list(results)),
        "data": results
        # TODO num_upcoming_shows
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    data = Venue.query.get_or_404(int(venue_id))
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    formData = VenueForm(request.form)
    try:
        # Venue.
        name = formData.name.data
        city = formData.city.data
        state = formData.state.data
        address = formData.address.data
        phone = formData.phone.data,
        genres = ',' .join(request.form.getlist('genres'))
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres)
        print('venue', venue)
        db.session.add(venue)
        db.session.commit()
        flash(request.form)
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
        print('error ==>', e)
        db.session.rollback()
        flash('Error while creating Venue')
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get_or_404(int(venue_id))
        Venue.query.get(int(venue_id)).delete()
        db.session.commit()
        flash('successfully deleted venue')
        return redirect(url_for('index'))
    except Exception as e:
        print('error ==>', e)
        flash('Venue not found.', e)
        return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = f"%{request.form.get('search_term', '')}%"
    results = Artist.query.filter(Artist.name.ilike(search_term))
    response = {
        "count": len(list(results)),
        "data": results
        # TODO num_upcoming_shows
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get_or_404(int(artist_id))
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(int(artist_id))
    form = ArtistForm(
        name=artist.name,
        city=artist.city,
        state=artist.state,
        phone=artist.phone,
        image_link=artist.image_link,
        genres=artist.genres,
        facebook_link=artist.facebook_link,
        website_link=artist.website_link,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description
    )

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    fields = ['name', 'city', 'state', 'phone', 'image_link', 'genres', 'facebook_link', 'website_link',
              'seeking_venue', 'seeking_description']
    form = ArtistForm(request.form)
    artist = Artist.query.get_or_404(int(artist_id))
    for field in fields:
        attr = getattr(form, field).data
        setattr(artist, field, attr)
    db.session.commit()
    flash('successfully updated artist')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(int(venue_id))
    form = VenueForm(
        name=venue.name,
        city=venue.city,
        state=venue.state,
        address=venue.address,
        phone=venue.phone,
        image_link=venue.image_link,
        genres=venue.genres,
        facebook_link=venue.facebook_link,
        website_link=venue.website_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description
    )

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # venue record with ID <venue_id> using the new attributes
    fields = ['name', 'city', 'state', 'address', 'phone', 'image_link', 'genres', 'facebook_link', 'website_link',
              'seeking_talent', 'seeking_description']
    form = VenueForm(request.form)
    venue = Venue.query.get_or_404(int(venue_id))
    for field in fields:
        attr = getattr(form, field).data
        setattr(venue, field, attr)
    db.session.commit()
    flash('successfully updated venue')
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

    formData = ArtistForm(request.form)
    try:
        name = formData.name.data
        city = formData.city.data
        state = formData.state.data
        phone = formData.phone.data
        image = formData.image_link.data
        genres = formData.genres.data
        facebook = formData.facebook_link.data
        website = formData.website_link.data
        seeking_venue = formData.seeking_venue.data
        seeking_description = formData.seeking_description.data

        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            image_link=image,
            facebook_link=facebook,
            website_link=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description
        )

        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
        print('e', e)
        flash('An error occurred. Artist ' + formData.name.data + ' could not be listed.')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    try:
        shows = Show.query.all()
        for show in shows:
            data.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })
        return render_template('pages/shows.html', shows=data)
    except Exception as e:
        print('e', e)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    formData = ShowForm()
    return render_template('forms/new_show.html', form=formData)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    formData = ShowForm(request.form)
    try:
        artist = Artist.query.get(int(formData.artist_id.data))
        venue = Venue.query.get(int(formData.venue_id.data))
        artist and venue
        show = Show(start_date=formData.start_time.data)
        artist.shows.append(show)
        venue.shows.append(show)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
        print('e', e)
        flash('An error occurred. Show could not be listed.')
        return redirect(url_for('create_shows'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''