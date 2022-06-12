#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:6000/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    genres = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='Artist', lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))


db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


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
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []

    for venue in Venue.query.with_entities(Venue.city, Venue.state).order_by(Venue.city).distinct():
        venue_obj = []
        for my_venue in Venue.query.filter_by(city=venue[0], state=venue[1]).all():
            temp_venues = {
                "id": my_venue.id,
                "name": my_venue.name,
                "num_upcoming_shows": 0
              }
            venue_obj.append(temp_venues)
            tem_data = {
              "city": venue[0],
              "state": venue[1],
              "venues": venue_obj
            }

        data.append(tem_data)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    search_word = "%{}%".format(search_term)

    result_venues = Venue.query.filter(Venue.name.ilike(search_word)).all()

    count_result = 0
    response = {
      "count": len(result_venues),
      "data": []
    }

    for venue in result_venues:
        temp_data = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": count_result,
        }

        response['data'].append(temp_data)

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    my_venue = Venue.query.get(venue_id)
    my_genres = my_venue.genres.replace("{", "").replace("}", "")

    data = {
      "id": venue_id,
      "name": my_venue.name,
      "genres": my_genres.split(","),
      "address": my_venue.address,
      "city": my_venue.city,
      "state": my_venue.state,
      "phone": my_venue.phone,
      "website": my_venue.website_link,
      "facebook_link": my_venue.facebook_link,
      "seeking_talent": my_venue.seeking_talent,
      "seeking_description": my_venue.seeking_description,
      "image_link": my_venue.image_link,
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count": 0,
      "upcoming_shows_count": 0,
    }

    for upcoming_show in my_venue.shows:
        artist = Artist.query.get(upcoming_show.venue_id)
        if datetime.strptime(upcoming_show.start_time, "%Y-%m-%d %H:%M:%S") > datetime.now():
            data["upcoming_shows"].append({
              "artist_id": upcoming_show.venue_id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": upcoming_show.start_time
            })

        data['upcoming_shows_count'] = len(data['upcoming_shows'])

    for past_show in my_venue.shows:
        artist = Artist.query.get(past_show.venue_id)
        if datetime.strptime(past_show.start_time, "%Y-%m-%d %H:%M:%S") < datetime.now():
            data["past_shows"].append({
              "artist_id": past_show.venue_id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": past_show.start_time
            })

        data['past_shows_count'] = len(data['past_shows'])

    data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
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
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success

    try:
        add_venue = Venue(name=request.form['name'], city=request.form['city'],
                          state=request.form['state'], address=request.form['address'],
                          genres=request.form.getlist('genres'),
                          website_link=request.form['website_link'],
                          phone=request.form['phone'], image_link=request.form['image_link'],
                          facebook_link=request.form['facebook_link'])

        db.session.add(add_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        print('in except')
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    for artist in Artist.query.all():
        one_artist = {
          "id": artist.id,
          "name": artist.name
        }
        data.append(one_artist)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    search_word = "%{}%".format(search_term)

    result_artists = Artist.query.filter(Artist.name.ilike(search_word)).all()

    count_result = 0
    response = {
      "count": len(result_artists),
      "data": []
    }

    for venue in result_artists:
        temp_data = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": count_result,
        }

        response['data'].append(temp_data)
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    my_artist = Artist.query.get(artist_id)

    my_genres = my_artist.genres.replace("{", "").replace("}", "")
    my_genres.split(","),

    data = {
      "id": artist_id,
      "name": my_artist.name,
      "genres": my_genres.split(","),
      "city": my_artist.city,
      "state": my_artist.state,
      "phone": my_artist.phone,
      "website": my_artist.website_link,
      "facebook_link": my_artist.facebook_link,
      "seeking_venue": my_artist.seeking_venue,
      "seeking_description": my_artist.seeking_description,
      "image_link": my_artist.image_link,
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count": 0,
      "upcoming_shows_count": 0,
    }
    for past_show in my_artist.shows:
        venue = Venue.query.get(past_show.venue_id)
        if datetime.strptime(past_show.start_time, "%Y-%m-%d %H:%M:%S") > datetime.now():
            data["upcoming_shows"].append({
              "venue_id": past_show.venue_id,
              "venue_name": venue.name,
              "venue_image_link": venue.image_link,
              "start_time": past_show.start_time
            })

        data['upcoming_shows_count'] = len(data['upcoming_shows'])
    for past_show in my_artist.shows:
        venue = Venue.query.get(past_show.venue_id)
        if datetime.strptime(past_show.start_time, "%Y-%m-%d %H:%M:%S") < datetime.now():
            data["past_shows"].append({
              "venue_id": past_show.venue_id,
              "venue_name": venue.name,
              "venue_image_link": venue.image_link,
              "start_time": past_show.start_time
            })

        data['past_shows_count'] = len(data['past_shows'])

    my_data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
    return render_template('pages/show_artist.html', artist=my_data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    my_artist = Artist.query.get(artist_id)
    my_genres = my_artist.genres.replace("{", "").replace("}", "")

    artist = {
      "id": artist_id,
      "name": my_artist.name,
      "genres": my_genres.split(","),
      "city": my_artist.city,
      "state": my_artist.state,
      "phone": my_artist.phone,
      "website_link": my_artist.website_link,
      "facebook_link": my_artist.facebook_link,
      "seeking_venue": my_artist.seeking_venue,
      "seeking_description": my_artist.seeking_description,
      "image_link": my_artist.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    seeking_venue = request.form.get('seeking_venue')
    is_seeking = False
    if seeking_venue:
        is_seeking = True
    else:
        pass

    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form['facebook_link']
        artist.website_link = request.form['website_link']
        artist.image_link = request.form['image_link']
        artist.seeking_venue = is_seeking
        artist.seeking_description = request.form['seeking_description']
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully changed!')
    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be changed.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    my_venue = Venue.query.get(venue_id)
    my_genres = my_venue.genres.replace("{", "").replace("}", "")
    my_genres.split(","),
    # TODO: populate form with values from venue with ID <venue_id>
    venue = {
      "id": venue_id,
      "name": my_venue.name,
      "genres":  my_genres.split(","),
      "address": my_venue.address,
      "city": my_venue.city,
      "state": my_venue.state,
      "phone": my_venue.phone,
      "website_link": my_venue.website_link,
      "facebook_link": my_venue.facebook_link,
      "seeking_talent": my_venue.seeking_talent,
      "seeking_description": my_venue.seeking_description,
      "image_link": my_venue.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing

    seeking_talent = request.form.get('seeking_venue')
    is_seeking = False
    if seeking_talent:
        is_seeking = True
    else:
        pass
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']
        venue.website_link = request.form['website_link']
        venue.seeking_venue = is_seeking
        venue.seeking_description = request.form['seeking_description']
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully changed!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be changed.')
    finally:
        db.session.close()
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

    seeking_venue = request.form.get('seeking_venue')

    is_seeking = False
    if seeking_venue:
        is_seeking = True
    else:
        pass
    try:
        artist = Artist(name=request.form['name'], city=request.form['city'],
                        state=request.form['state'], phone=request.form['phone'],
                        genres=request.form.getlist('genres'), facebook_link=request.form['facebook_link'],
                        website_link=request.form['website_link'],
                        image_link=request.form['image_link'],
                        seeking_venue=is_seeking,
                        seeking_description=request.form['seeking_description'])
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    all_shows = Show.query.all()

    for show in all_shows:
        venue_id = Venue.query.get(show.venue_id)
        artist_id = Artist.query.get(show.artist_id)

        data.append({
          "venue_id": show.venue_id,
          "venue_name": venue_id.name,
          "artist_id": show.artist_id,
          "artist_name": artist_id.name,
          "artist_image_link": artist_id.image_link,
          "start_time": show.start_time
        })

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

    try:
        add_show = Show(artist_id=request.form['artist_id'],
                        venue_id=request.form['venue_id'],
                        start_time=request.form['start_time'],)

        db.session.add(add_show)
        db.session.commit()
        flash('Show was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    # on successful db insert, flash success

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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    port = int(os.environ.get('PORT', 3000))
    app.run(host='127.0.0.1', port=port)
'''
