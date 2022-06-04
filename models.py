from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), nullable=False, default=True, server_default="true")
    seeking_description = db.Column(db.Text(), nullable=True)
    shows = db.relationship('Show', backref='venue', lazy=True, cascade="all, delete", passive_deletes=True)

    @property
    def upcoming_shows(self):
        return list(filter(lambda x: x.start_date > datetime.utcnow(), self.shows))

    @property
    def past_shows(self):
        return list(filter(lambda x: x.start_date < datetime.utcnow(), self.shows))

    @property
    def past_shows_count(self):
        return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)

    @property
    def num_upcoming_shows(self):
        return self.upcoming_shows_count


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), default={}, nullable=False, server_default='{}')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean(), nullable=False, default=True, server_default="true")
    seeking_description = db.Column(db.Text(), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    @property
    def upcoming_shows(self):
        return list(filter(lambda x: x.start_date > datetime.utcnow(), self.shows))

    @property
    def past_shows(self):
        return list(filter(lambda x: x.start_date < datetime.utcnow(), self.shows))

    @property
    def past_shows_count(self):
        return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)

    @property
    def num_upcoming_shows(self):
        return self.upcoming_shows_count


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime(), default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))

    @property
    def start_time(self):
        return str(self.start_date)