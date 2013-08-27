''' GAE data model definitions using NDB.

	Reference: http://bit.ly/HncnND
	Cheat Sheet: http://bit.ly/130q3f1
	Relationships: http://bit.ly/SFQQrl
'''

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from geo.geomodel import GeoModel

class Country(GeoModel, ndb.Model):
	''' Models a country after ISO 3166-1.
		See http://en.wikipedia.org/wiki/ISO_3166-1 for more. '''
	display_name = ndb.StringProperty(required = True)

class Subdivision(GeoModel, ndb.Model):
	''' Models a country's subdivision such as state or province. 
		Modeled after ISO 3166-2; see http://en.wikipedia.org/wiki/ISO_3166-2
		for more.'''
	display_name = ndb.StringProperty(required = True)

	@classmethod
	def query_location(cls, ancestor_key):
		return cls.query(ancestor = ancestor_key)

class Locality(GeoModel, ndb.Model):
	''' Models a locality such as city or town. '''
	display_name = ndb.StringProperty(required = True)

	@classmethod
	def query_location(cls, ancestor_key):
		return cls.query(ancestor = ancestor_key)

class Contact(polymodel.PolyModel):
	''' Superclass that defines common contact properties. '''
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_edited = ndb.DateTimeProperty(auto_now = True)

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
	def instagram(self):
		return Instagram.query(Instagram.contact == self.key)

	@property
	def foursquare(self):
		return Foursquare.query(Foursquare.contact == self.key)

	@property
	def facebook(self):
		return Facebook.query(Facebook.contact == self.key)

	@property
	def twitter(self):
		return Twitter.query(Twitter.contact == self.key)

	@property
	def tumblr(self):
		return Tumblr.query(Tumblr.contact == self.key)

	@property
	def address(self):
		return Address.query(Address.contact == self.key)

	@property
	def mailing_address(self):
		return MailingAddress.query(MailingAddress.contact == self.key)

	def props(self):
		# for a bit of background on this method, see http://bit.ly/19yzgya
		return dict(self._properties.items() + {attr_name:getattr(self,attr_name) for \
							attr_name, attr_value in \
							Contact.__dict__.iteritems() if \
							isinstance(attr_value,property)}.items())

	@classmethod
	def prop_names(cls):
		return {attr_name for attr_name, attr_value \
						  in cls.__dict__.iteritems() \
						  if isinstance(attr_value,property)}

class Email(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	email = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Phone(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	phone_type = ndb.StringProperty(choices=('home', 'work', 'fax', 'mobile', 'other'))
	country_code = ndb.StringProperty()
	number = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Website(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)
	
	url = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Gallery(Website):
	contact = ndb.KeyProperty(kind=Contact)	

class Instagram(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	instagram = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Foursquare(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	foursquare = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Facebook(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	facebook = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Twitter(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	twitter = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Tumblr(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	tumblr = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Address(GeoModel, ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	street = ndb.StringProperty()
	locality = ndb.StringProperty()
	subdivision = ndb.StringProperty()
	country = ndb.StringProperty()
	postal_code = ndb.StringProperty()
	intersection = ndb.StringProperty()

class MailingAddress(Address):
	contact = ndb.KeyProperty(kind=Contact)

class Studio(Contact):
	''' Models a physical tattoo studio. '''
	name = ndb.StringProperty()

	# Returns all studios in a given location
	# Location is defined by country > subdivision (e.g. state or province) > 
	# locality (e.g. city or town) 
	@classmethod
	def query_location(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key)
	
	# Return all StudioArtist relationships assigned to studio
	@property
	def artists(self):
		return StudioArtist.gql('WHERE studio = :1', self.key)

class Artist(Contact):
	''' Models a tattoo artist. '''
	display_name = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	
	# Return all StudioArtist relationships assigned to artist
	@property
	def studios(self):
		return StudioArtist.gql('WHERE artist = :1', self.key)

class StudioArtist(ndb.Model):
	''' Models the N-to-N relationship between Studio and Artist. '''
	studio = ndb.KeyProperty(required=True, kind=Studio)
	artist = ndb.KeyProperty(required=True, kind=Artist)

	relationship = ndb.StringProperty(choices=('owner', 'artist', 'guest'))