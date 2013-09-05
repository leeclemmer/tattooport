import re
import time
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'lib'))

import urllib
import urllib2
import json
import logging
import hashlib

# internal
import keys
import utils
import deferred_tasks
from countries import COUNTRIES
from utils import info
from models import *


# external
import webapp2
import jinja2
import mapq
import general_counter
from instagram.client import InstagramAPI
from google.appengine.api import memcache
from google.appengine.ext import deferred


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   extensions = ['jinja2.ext.loopcontrols'],
							   autoescape = True)

unauthenticated_api = InstagramAPI(client_id=keys.IG_CLIENTID,
										  client_secret=keys.IG_CLIENTSECRET,
										  redirect_uri=keys.IG_REDIRECTURI)

def make_secure_val(value):
	return '%s|%s' % (value, hashlib.sha256(keys.SECRET + value).hexdigest())

def check_secure_val(secure_val):
	user_id = secure_val.split('|')[0]
	if secure_val == make_secure_val(user_id):
		return user_id

class BaseHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def str_to_class(self, s):
		''' Return a class with name s. '''
		return getattr(sys.modules[__name__], s)

	def key_to_path(self, key):
		''' Converts a key with ancestors to a url path. '''
		return '/%s' % ('/'.join([urllib.quote_plus(str(pair[1])) for pair in key.pairs()]),)

	def path_to_key(self, path):
		''' Converts path to key with ancestor path. '''
		ancestor_kinds = ['Country','Subdivision','Locality','Contact']
		if path.isdigit():
			return ndb.Key('Contact',int(path))
		else:
			return ndb.Key(pairs=zip(ancestor_kinds,
								[int(c) if c.isdigit() \
										else c for c in \
										urllib.unquote_plus(path).split('/')]))

	def path_to_breadcrumbs(self, path):
		''' Converts a path to a list of breadcrumbs 
			in the form [['Counntry/Subdivision/Locality.display_name','browse path']] '''
		paths = [path,]
		while '/' in path:
			paths.insert(0,path.rsplit('/',1)[0])
			path = path.rsplit('/',1)[0]
		
		return zip([self.path_to_key(p).get().display_name
					 	if self.path_to_key(p).kind() != 'Contact' 
					 	else self.path_to_key(p).get().name
					 		for p in paths],paths)

	def num_fields(self, args):
		''' Returns dictionary of how many Contact.prop_names in args 
			there are for each arg. '''		
		return {field:len([arg for arg in args if arg.startswith(field)]) \
				for field in Contact.prop_names()}

	def geo_pt(self, address):
		''' Returns ndb.GeoPt for given address.'''
		try:
			mapq.key(keys.MAPQUEST_API_KEY)
			latlng = mapq.latlng(address)
			return ndb.GeoPt(latlng['lat'],latlng['lng'])
		except:
			utils.log_tb()
			return None

	def static_map_url(self, geo_pt, height=200, width=200):
		base_url = 'http://maps.googleapis.com/maps/api/staticmap?'
		if not hasattr(geo_pt,'lat'): return None
		else: return '%ssize=%sx%s&markers=%s,%s&sensor=false&key=%s' % \
				(base_url,
					width,
					height, 
					geo_pt.lat, 
					geo_pt.lon,
					keys.GMAPS_STATIC_API_KEY)	

	@classmethod
	def regions_in_db(cls):
		''' Returns a list of list of lists with all used regions. '''
		return [[country,
					[[subdivision,
						[[locality,urllib.quote_plus(locality.key.id())] for locality in Locality.query_location(subdivision.key).order(Locality.display_name).fetch()]]
					for subdivision in Subdivision.query_location(country.key).order(Subdivision.display_name).fetch()]]
				for country in Country.query().order(Country.display_name).fetch()]

	def read_secure_cookie(self, name):
		value = self.request.cookies.get(name)
		return value and check_secure_val(value)

	def set_secure_cookie(self, name, value):
		cookie_value = make_secure_val(value)
		self.response.headers.add_header('Set-Cookie','%s=%s; Path=/' % \
										 (name, cookie_value))

	def logged_in_user(self):
		user_id = self.read_secure_cookie('user_id')
		if user_id:
			user = memcache.get(user_id)
			if user is not None:
				return user
			else:
				user = InstagramUser.by_id(int(user_id))
				memcache.set(user_id, user, time=60*30)
				return user
		else: return None

	@classmethod
	def get_instagram_api(cls,access_token=''):
		''' Helper function for quick access to instagram api. 
			Access token optional. If not given, API access is limited.
		'''
		return InstagramAPI(client_id=keys.IG_CLIENTID,
							client_secret=keys.IG_CLIENTSECRET,
							access_token=access_token)

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key.id()))

	def logoff(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		self.user = self.logged_in_user()

class FourOhFour(BaseHandler):
	def get(self):
		self.render('404.html',
					user=self.user)

class Home(BaseHandler):
	def get(self):
		if not self.user:
			self.redirect('/login')
		else:
			self.render('home.html',
						user=self.user)

class Login(BaseHandler):
	def get(self):
		error = self.request.get('error')
		error_reason = self.request.get('error_reason')
		error_description = self.request.get('error_description')

		code = self.request.get('code')

		if error:
			logging.error('''Error: %s\n
							 Error reason: %s\n
							 Error description: %s\n''' % (error,
							 							   error_reason,
							 							   error_description))
			error_message = '''To use TattooPort, you have to sign in using your Instagram credentials. <a href="/">Return home to try again</a>'''
			self.render('error.html',
						title='Login Error',
						error_message=error_message
						)
		elif code:
			try:
				access_token = unauthenticated_api.exchange_code_for_access_token(code)
				if not access_token:
					error_message = '''Uh oh, looks like we had a problem logging you in via Instagram. <a href="/">Return home to try again</a>'''
					self.render('error.html',
								title='Login Error',
								error_message=error_message
								)
				elif access_token:
					api = InstagramAPI(access_token=access_token[0])
					user_id = api.user().id
					user_name = api.user().username
					full_name = api.user().full_name
					profile_picture = api.user().profile_picture

					instagram_user = InstagramUser.by_ig_id(user_id).get()
					if not instagram_user:
						# First time user
						instagram_user = InstagramUser.register(
											   user_name=user_name,
											   user_id=user_id,
											   full_name=full_name,
											   profile_picture=profile_picture,
											   access_token=access_token
											   )
					else:
						# Existing user, update information
						instagram_user.user_name = user_name
						instagram_user.full_name = full_name
						instagram_user.profile_picture = profile_picture
						instagram_user.access_token = access_token[0]
					instagram_user.put()

					self.login(instagram_user)
					self.redirect('/')
			except:
				utils.log_tb()
		elif self.user:
			self.redirect('/')
		else:
			try:
				authentication_url = unauthenticated_api.get_authorize_url(scope=['likes','comments','relationships'])
			except:
				utils.log_tb()
			self.render('login.html',
						 authentication_url=authentication_url)

class Logoff(BaseHandler):
	def get(self):
		self.logoff()
		self.redirect('/')

class ShopsArtists(BaseHandler):
	def get(self):
		regions = self.regions_in_db()
		localities = []

		for country in regions:
			if country[0].key.id() == 'US':
				for subdivision in country[1]:
					for locality in subdivision[1]:
						locality.append(self.key_to_path(locality[0].key))
						localities.append(locality)

		localities.sort(key=lambda x: x[0].display_name)

		self.render('shops_artists.html',
					user=self.user,
					localities=localities)

class LocalityPage(BaseHandler):
	def get(self, pagename):
		if pagename.endswith('/'): pagename = pagename[:-1]

		locality = self.path_to_key(pagename).get()
		
		# Prevent user from URL hacking
		if pagename.count('/') is not 2:
			self.redirect('/shops-artists')

		# Fetch shops
		region_pt = locality.location
		try:
			results = Address.proximity_fetch(
				Address.query(),
				region_pt,
				max_results=10,
				max_distance=80467)
		except AttributeError:
			utils.catch_exception()
			results = ''
		results = sorted([addr.contact.get() for addr in results], key=lambda x: x.name)
		results = zip(results, [urllib.quote_plus(result.name) for result in results ])

		self.render('locality.html',
					user=self.user,
					locality=locality,
					results=results)

class ShopPage(BaseHandler):
	def get(self, pagename):
		shop_name, sid = pagename.split('/')
		shop_name = urllib.unquote_plus(shop_name)
		shop = self.get_shop(shop_name, sid)

		if not self.user:
			# Anonymous User
			media = memcache.get(pagename)
			if not media:
				# kick off cron-job to refresh cache
				#info('refresh_cache',refresh_cache())
				deferred.defer(deferred_tasks.refresh_cache)
			else:
				media = media[:12]

			self.render('shop.html',
						user=self.user,
						shop=shop,
						media=media,
						next=None)
		else:
			# Logged in user
			api = self.get_instagram_api(access_token=self.user.access_token)

			media, next = self.get_shop_response(api, shop_name)

			self.render('shop.html',
						user=self.user,
						shop=shop,
						media=media,
						next=next)

	@classmethod
	def get_shop(cls, shop_name, sid):		
		# If shops with the same name, compare IDs
		# There is chance of same ID and same name... 
		# ... very remote (let's hope)
		for s in Studio.by_name(shop_name):
			if int(sid) == s.key.id():
				return s
				break

	@classmethod
	def get_shop_response(cls, api, shop, sid):
		media = None
		next = None
		if shop.instagram.get() is not None:
			for ig in shop.instagram.fetch():
				if ig.primary == True and ig.user_id:
					media, next = api.user_recent_media(
						user_id=ig.user_id,
						count=30)
					break
		elif shop.foursquare.get() is not None:
			for fsq in shop.foursquare.fetch():
				if fsq.primary == True and fsq.location_id:
					location_id = fsq.location_id
					media, next = api.location_recent_media(
						count=30, 
						location_id=fsq.location_id)
					break

		return (media, next)

app = webapp2.WSGIApplication([('/?',Home),
							   ('/login', Login),
							   ('/logoff', Logoff),
							   ('/shops-artists', ShopsArtists),
							   ('/shop/?(.*)?', ShopPage),
							   ('/loc/?(.*)?', LocalityPage),
							   ('/.*', FourOhFour)], debug = True)