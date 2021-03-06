''' GAE data model definitions using NDB.

	Reference: http://bit.ly/HncnND
	Cheat Sheet: http://bit.ly/130q3f1
	Relationships: http://bit.ly/SFQQrl
'''
import urllib
import cPickle

from utils import info

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from geo.geomodel import GeoModel

# Helper functions

def regions_in_db():
	''' Returns a list of list of lists with all used regions. '''
	return [[country,
				[[subdivision,
					[[locality,urllib.quote_plus(locality.key.id())] for locality in Locality.query_location(subdivision.key).order(Locality.display_name).fetch()]]
				for subdivision in Subdivision.query_location(country.key).order(Subdivision.display_name).fetch()]]
			for country in Country.query().order(Country.display_name).fetch()]

def locality_keys_in_db():
	''' Returns a list of all locality keys used in db. '''
	return KeyList.get_by_id('Localities').key_list

def parent_key(group_name, group):
	return ndb.Key('%s' % group_name,group)


# Models

class KeyList(ndb.Model):
	''' Generic model containing lists of keys. '''
	key_list = ndb.KeyProperty(repeated=True)

class StringList(ndb.Model):
	''' Generic model containing lists of strings. '''
	string_list = ndb.StringProperty(repeated=True)

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

	@classmethod
	def by_ig_username(cls, ig_username):
		ig = Instagram.query(Instagram.instagram == ig_username).get()
		if ig:
			return ig.contact
		else:
			return None

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
	user_id = ndb.StringProperty()
	profile_picture = ndb.StringProperty()
	primary = ndb.BooleanProperty()

class Foursquare(ndb.Model):
	contact = ndb.KeyProperty(kind=Contact)

	foursquare = ndb.StringProperty()
	location_id = ndb.StringProperty()
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

	@classmethod
	def by_name(self, name):
		return Studio.query(Studio.name == name).fetch()

class Artist(Contact):
	''' Models a tattoo artist. '''
	display_name = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	
	# Return all StudioArtist relationships assigned to artist
	@property
	def studios(self):
		return StudioArtist.gql('WHERE artist = :1', self.key)

	@classmethod
	def by_name(self, name):
		return Artist.query(Artist.display_name == name).fetch()

class StudioArtist(ndb.Model):
	''' Models the N-to-N relationship between Studio and Artist. '''
	studio = ndb.KeyProperty(required=True, kind=Studio)
	artist = ndb.KeyProperty(required=True, kind=Artist)

	relationship = ndb.StringProperty(choices=('owner', 'artist', 'guest'))

class TattooGroup(ndb.Model):
	''' Models a tattoo group, like "Animals" '''
	name = ndb.StringProperty(required=True)

	@classmethod
	def all_groups(cls):		
		groups = cls.query().order(cls.name).fetch()
		return [[group,[category for category in \
						TattooCategory.by_group(group.name).fetch()]] for group in groups]

class TattooCategory(ndb.Model):
	''' Models a tattoo category, like "old school tattoo" '''
	name = ndb.StringProperty(required=True)

	instagram_tag = ndb.StringProperty()
	instagram_count = ndb.IntegerProperty()

	@classmethod
	def by_id(cls, uid, group):
		return TattooCategory.get_by_id(uid, parent=parent_key('TattooGroup',
			group))

	@classmethod
	def by_name(cls, name):
		return TattooCategory.query(TattooCategory.name == name)

	@classmethod
	def by_group(cls, group):
		return TattooCategory.query(ancestor=parent_key('TattooGroup',group))

class User(ndb.Model):
	''' Models a user. '''
	user_name = ndb.StringProperty(required=True)

	@classmethod
	def by_id(cls, uid, group='default'):
		return User.get_by_id(uid, parent=parent_key('users',group))

	@classmethod
	def by_name(cls, name):
		return User.query(User.user_name == name)

class InstagramUser(User):
	''' Models an Instagram user. '''
	user_id = ndb.StringProperty(required=True)
	full_name = ndb.StringProperty()
	profile_picture = ndb.StringProperty()
	access_token = ndb.StringProperty()

	@classmethod
	def by_id(cls, uid, group='default'):
		return InstagramUser.get_by_id(uid, parent=parent_key('users',group))

	@classmethod
	def by_ig_id(cls, uid):
		return InstagramUser.query(InstagramUser.user_id == uid)

	@classmethod
	def register(cls, user_name, user_id, 
				 full_name=None, profile_picture=None,
				 access_token=access_token, group='default'):
		return InstagramUser(parent=parent_key('users',group),
							 user_name=user_name,
							 user_id=user_id,
							 full_name=full_name,
							 profile_picture=profile_picture,
							 access_token=access_token)

class PopularList(ndb.Model):
	popular_list = ndb.BlobProperty(required=True)

	@classmethod
	def put_pop_list(cls, plid, pl):
		try:
			result = cPickle.dumps(pl)
			PopularList(id=plid, 
						popular_list=result).put()
		except cPickle.PicklingError, e:
			info('PicklingError', e)

	@classmethod
	def get_pop_list(cls, plid):
		try:
			pl = PopularList.get_by_id(plid)
			if pl:
				value = cPickle.loads(str(pl.popular_list))
			else: value = None
			return value
		except cPickle.PicklingError, e:
			info('PicklingError', e)