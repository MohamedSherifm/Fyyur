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
from flask_migrate import Migrate
from forms import *
from sqlalchemy import func , ARRAY
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show' , backref='venue' , lazy = True)
    def __repr__(self):
      return f'<Todo {self.id} {self.name}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show' , backref='artist' , lazy = True)




   


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer , primary_key = True)
  start_time = db.Column(db.DateTime , nullable = False )
  artist_id = db.Column(db.Integer , db.ForeignKey('artist.id'))
  venue_id = db.Column(db.Integer , db.ForeignKey('venue.id'))

  

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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




  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  allVuenues=Venue.query.with_entities(func.count(Venue.name),Venue.city, Venue.state ,).group_by(Venue.state , Venue.city).all()
  print(len(allVuenues))



  for i in allVuenues:
    x = Venue.query.filter_by(state=i.state).all()
    s=[]
    for n in x :
      s.append({"id":n.id , "name":n.name , "num_upcoming_shows":Show.query.filter((Show.venue_id==n.id)&(Show.start_time>datetime.now())).count() })
    data.append({"city":i.city , "state":i.state , "venues":s})

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term')
  res = Venue.query.filter(Venue.name.ilike('%{}%'.format(search))).all() 
  count = len(res)
  data = []
  for i in res:
    data.append({"id":i.id , "name" : i.name , "num_upcoming_shows":Show.query.filter((Show.venue_id==i.id)&(Show.start_time>datetime.now())).count})
    
  response={"count":count , "data":data}  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows=[]
  upcoming_shows=[]
  past = Show.query.filter((Show.venue_id==venue_id)&(Show.start_time<datetime.now())).all()
  for i in past:
    past_shows.append({"artist_id":i.artist.id , "artist_name" :i.artist.name , "artist_image_link":i.artist.image_link ,
    "start_time" : i.start_time.strftime("%Y-%m-%d %H:%M:%S")})

  upcoming = Show.query.filter((Show.venue_id==venue_id)&(Show.start_time>datetime.now())).all()
  for i in upcoming:
    upcoming_shows.append({"artist_id":i.artist.id , "artist_name":i.artist.name , "artist_image_link":i.artist.image_link ,
     "start_time":i.start_time.strftime("%Y-%m-%d %H:%M:%S")})
    

  y = Venue.query.filter(Venue.id==venue_id).all()
  
  data={"id":y[0].id , "name":y[0].name ,"genres":y[0].genres , "address":y[0].address ,"city":y[0].city ,"state":y[0].state
 ,"phone":y[0].phone , "website":y[0].website , "facebook_link":y[0].facebook_link , "seeking_talent":y[0].seeking_talent, 
 "seeking_description":y[0].seeking_description ,"image_link":y[0].image_link , "past_shows":past_shows , "up_coming_shows":upcoming_shows
 ,"past_shows_count":len(past) , "upcoming_shows_count":len(upcoming)}


  
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  error = False
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  name = request.form['name']
  phone = request.form['phone']
  address = request.form['address']
  city = request.form['city']
  state = request.form['state']
  genres = request.form.getlist('genres')
  #facebook_link = request.form['facebook_link']

  try:
    venue = Venue(name = name , phone = phone , address = address , city = city , state = state , genres = ['jazz' , 'classic'] , facebook_link = 'www.facebook2.com', website='' , seeking_talent = False , seeking_description='' , image_link='')
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close
  if error:
    flash('Venue ' + request.form['name'] + ' was not added')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
        


  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False 
  try :
    venue = Venue.query.filter(Venue.id==venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close
  if error:
    flash('Venue ' + venue[0].name + ' was not deleted')
  else:
    flash('Venue ' + venue[0].name + ' was successfully deleted')  


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  allArtist = Artist.query.all()
  for i in allArtist:
    data.append({"id":i.id , "name":i.name})



  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term')
  res = Artist.query.filter(Artist.name.ilike('%{}%'.format(search))).all() 
  count = len(res)
  data = []
  for i in res:
    data.append({"id":i.id , "name" : i.name , "num_upcoming_shows":Show.query.filter((Show.artist_id==i.id)&(Show.start_time>datetime.now())).count})
    
  response={"count":count , "data":data}  
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows=[]
  upcoming_shows=[]
  past = Show.query.filter((Show.artist_id==artist_id)&(Show.start_time<datetime.now())).all()
  for i in past:
    past_shows.append({"venue_id":i.venue.id , "venue_name" :i.venue.name , "venue_image_link":i.venue.image_link ,
    "start_time" : i.start_time.strftime("%Y-%m-%d %H:%M:%S")})

  upcoming = Show.query.filter((Show.artist_id==artist_id)&(Show.start_time>datetime.now())).all()
  for i in upcoming:
    upcoming_shows.append({"venue_id":i.venue.id , "venue_name":i.venue.name , "venue_image_link":i.venue.image_link ,
     "start_time":i.start_time.strftime("%Y-%m-%d %H:%M:%S")})
    

  y = Artist.query.filter(Artist.id==artist_id).all()
  
  data={"id":y[0].id , "name":y[0].name ,"genres":y[0].genres  ,"city":y[0].city ,"state":y[0].state
 ,"phone":y[0].phone , "website":y[0].website , "facebook_link":y[0].facebook_link , "seeking_veune":y[0].seeking_venue, 
 "seeking_description":y[0].seeking_description ,"image_link":y[0].image_link , "past_shows":past_shows , "up_coming_shows":upcoming_shows
 ,"past_shows_count":len(past) , "upcoming_shows_count":len(upcoming)}


  
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.city.data = artist.city
  

  
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  error = False
  try:
    
    artist.name = request.form['name']
    artist.phone = request.form['phone']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.genres = request.form.getlist('genres')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Could not be updated')
  if not error:
    flash('Updated successfully')        




  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link
  form.city.data = venue.city
  form.address.data = venue.address
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.phone = request.form['phone']
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.genres = request.form.getlist('genres')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error :
    flash('Could not be updated')      
  if not error:
    flash('Updated successfully')  
  

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form['name']
  phone = request.form['phone']
  city = request.form['city']
  state = request.form['state']
  genres = request.form.getlist('genres')
  #facebook_link = request.form['facebook_link']

  try:
    artist = Artist(name = name , phone = phone , city = city , state = state , genres = genres , facebook_link = 'www.facebook/Ar2.com', website='' , seeking_venue = False , seeking_description='' , image_link='')
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Artist ' + request.form['name'] + ' was not added')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
        

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  shows = Show.query.all()
  for i in shows:
    data.append({"venue_id":i.venue.id , "venue_name":i.venue.name , "artist_id":i.artist.id , "artist_name":i.artist.name,
    "artist_image_link":i.artist.image_link , "start_time":i.start_time.strftime("%Y-%m-%d %H:%M:%S")})



  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  try :
    show = Show(artist_id = artist_id , venue_id = venue_id , start_time = start_time) 
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Show was not listed')
  if not error :
    flash('Show was successfully listed!')





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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
