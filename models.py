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
	pass

class Subdivision(ndb.Model):
	''' Models a country's subdivision such as state or province. 
		Modeled after ISO 3166-2; see http://en.wikipedia.org/wiki/ISO_3166-2
		for more.'''
	pass

class Locality(ndb.Model):
	''' Models a locality such as city or town. '''
	pass

class Contact(polymodel.PolyModel):
	''' Superclass that defines common contact properties. '''

	instagram_username = ndb.StringProperty()
	facebook_username = ndb.StringProperty()
	twitter_username = ndb.StringProperty()
	tumblr_username = ndb.StringProperty()

	@property
	def address(self):
		return Address.query(Address.contact == self.key())

	@property
	def email(self):
		return Email.query(Email.contact == self.key())

	@property
	def phone(self):
		return Phone.query(phone.contact == self.key())

	@property
	def website(self):
		return Website.query(website.contact == self.key())

class Address(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	address = ndb.StringProperty()
	locality = ndb.StringProperty()
	subdivision = ndb.StringProperty()
	country = ndb.StringProperty()
	postal_code = ndb.StringProperty()
	intersection = ndb.StringProperty()
	lat_lon = ndb.GeoPtProperty()

class Email(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	email = ndb.StringProperty()

class Phone(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)

	phone_type = ndb.StringProperty(choices = ('home', 'work', 'fax', 'mobile', 'other'))
	number = ndb.StringProperty()

class Website(ndb.Model):
	contact = ndb.KeyProperty(kind = Contact)
	
	url = ndb.StringProperty()

class Studio(Contact):
	''' Models a physical tattoo studio. '''
	name = ndb.StringProperty()

	# Returns all studios in a given location
	# Location is defined by country > subdivision (e.g. state or province) > 
	# locality (e.g. city or town) 
	@classmethod
	def query_location(cls, ancestor_key):
		return cls.query(ancestor = ancestor_key).order(cls.name)
	
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

