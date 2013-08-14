''' GAE data model definitions using NDB.

	Reference: http://bit.ly/HncnND
	Cheat Sheet: http://bit.ly/130q3f1
	Relationships: http://bit.ly/SFQQrl
'''

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

class Country(ndb.Model):
	''' Models a country after ISO 3166-1.
		See http://en.wikipedia.org/wiki/ISO_3166-1 for more. '''
	display_name = ndb.StringProperty(required = True)

class Subdivision(ndb.Model):
	''' Models a country's subdivision such as state or province. 
		Modeled after ISO 3166-2; see http://en.wikipedia.org/wiki/ISO_3166-2
		for more.'''
	display_name = ndb.StringProperty(required = True)

class Locality(ndb.Model):
	''' Models a locality such as city or town. '''
	display_name = ndb.StringProperty(required = True)

class Contact(polymodel.PolyModel):
	''' Superclass that defines common contact properties. '''
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_edited = ndb.DateTimeProperty(auto_now = True)

	@property
	def instagram_username(self):
		return InstagramUsername.query(InstagramUsername.contact == self.key)

	@property
	def facebook_username(self):
		return FacebookUsername.query(FacebookUsername.contact == self.key)

	@property
	def twitter_username(self):
		return TwitterUsername.query(TwitterUsername.contact == self.key)

	@property
	def tumblr_username(self):
		return TumblrUsername.query(TumblrUsername.contact == self.key)

	@property
	def address(self):
		return Address.query(Address.contact == self.key)

	@property
	def mailing_address(self):
		return MailingAddress.query(MailingAddress.contact == self.key)

	@property
	def email(self):
		return Email.query(Email.contact == self.key)

	@property
	def phone(self):
		return Phone.query(Phone.contact == self.key)

	@property
	def website(self):
		return Website.query(Website.contact == self.key)

	@property
	def gallery(self):
		return Gallery.query(Gallery.contact == self.key)

	@property
	def props(self):
		return dict(self._properties.items() + {
			'instagram_username':self.instagram_username,
		   'facebook_username':self.facebook_username,
		   'twitter_username':self.twitter_username,
		   'tumblr_username':self.tumblr_username,
		   'address':self.address,
		   'mailing_address':self.mailing_address,
		   'email':self.email,
		   'phone':self.phone,
		   'website':self.website,
		   'gallery':self.gallery
		   }.items())

class Email(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	email = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Phone(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	phone_type = ndb.StringProperty(choices = ('home', 'work', 'fax', 'mobile', 'other'))
	country_code = ndb.StringProperty()
	number = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Website(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)
	
	url = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Gallery(Website):
	contact = ndb.KeyProperty(kind = Contact)	

class InstagramUsername(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	instagram_username = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class FacebookUsername(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	facebook_username = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class TwitterUsername(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	twitter_username = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class TumblrUsername(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	tumblr_username = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Address(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	street = ndb.StringProperty()
	locality = ndb.StringProperty()
	subdivision = ndb.StringProperty()
	country = ndb.StringProperty()
	postal_code = ndb.StringProperty()
	intersection = ndb.StringProperty()
	lat_lon = ndb.GeoPtProperty()

class MailingAddress(Address):
	contact = ndb.KeyProperty(kind = Contact)

class Studio(Contact):
	''' Models a physical tattoo studio. '''
	name = ndb.StringProperty()

	# Returns all studios in a given location
	# Location is defined by country > subdivision (e.g. state or province) > 
	# locality (e.g. city or town) 
	@classmethod
	def query_location(cls, ancestor_key):
		return cls.query(ancestor = ancestor_key)
	
	# Return all artists assigned to studio
	@property
	def artists(self):
		return Artist.gql('WHERE studios = :1', self.key())

class Artist(Contact):
	''' Models a tattoo artist. '''
	artist_name = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()

	# N-to-N relationship to Studio
	studios = ndb.KeyProperty(repeated = True)

