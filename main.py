import re
import time
import os
import sys
import socket

import urllib
import urllib2
import json
import logging
import hashlib

# internal
import fix_path
import keys
import utils
import cache
from countries import COUNTRIES
from utils import info
from models import *
import helper


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

def format_number_with_commas(number):
	return '{:,}'.format(number)
jinja_env.filters['format_number_with_commas'] = format_number_with_commas

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

	def ig_url_params(self, access_token):		
		params = '?access_token=%s' % (access_token,)
		params += '&count=30'
		return params

	def ig_user_media_recent(self, shop, access_token):
		if shop.instagram.get():
			return '%s%s%s%s' % ('https://api.instagram.com/v1/users/',
								 shop.instagram.get().user_id,
								 '/media/recent/',
								 self.ig_url_params(access_token))
		else: return None

	def ig_location_media_recent(self, shop, access_token):
		if shop.foursquare.get():
			return '%s%s%s%s' % ('https://api.instagram.com/v1/locations/',
								 shop.foursquare.get().location_id,
								 '/media/recent/',
								 self.ig_url_params(access_token))
		else: return None

	def ig_tag_recent_media(self, category, access_token):
		if category and category.instagram_tag:
			return '%s%s%s%s' % ('https://api.instagram.com/v1/tags/',
								 category.instagram_tag,
								 '/media/recent',
								 self.ig_url_params(access_token))
		else: return None

	def json_output(self, *a, **kw):
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		if a: self.write(json.dumps(a[0], sort_keys=True, indent=4, separators=(',', ': ')))
		elif kw: self.write(json.dumps(kw))

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

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key.id()))

	def logoff(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		self.user = self.logged_in_user()

class FourOhFour(BaseHandler):
	def get(self, pagename):
		if pagename in ['shop','artist']:
			self.redirect('/shops-artists')
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

class Tattoos(BaseHandler):
	def get(self):
		self.render('tattoos.html',
					user=self.user,
					groups=TattooGroup.all_groups())

class TattooCategoryPage(BaseHandler):
	def get(self, pagename):
		parent, category_name = pagename.split('/')
		category_name = urllib.unquote_plus(category_name)
		category_name = ''.join(category_name.split(' '))
		category = ndb.Key('TattooGroup', parent, 
						   'TattooCategory', category_name).get()
		api_url = self.ig_tag_recent_media(category, self.user.access_token)
		self.render('tattoo_category.html',
					user=self.user,
					category=category,
					api_url=api_url)

class ShopsArtists(BaseHandler):
	def get(self):
		regions = regions_in_db()
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
		# Get Locality key
		if pagename.endswith('/'): pagename = pagename[:-1]
		locality = self.path_to_key(pagename.split('&')[0])
		
		# Prevent user from URL hacking
		if pagename.count('/') is not 2:
			self.redirect('/shops-artists')

		# Fetch shops
		shop_results = helper.nearby_shops(locality)

		# Fetch artists
		artist_results = helper.shops_artists(shop_results)		

		# Add encoded name to shop list
		shop_results = zip(shop_results, [urllib.quote_plus(result.name) for result in shop_results ])

		# Add path to artist list
		artist_results = zip(artist_results,[urllib.quote_plus(result.display_name) for result in artist_results])

		# Set cache url as api_url
		api_url = '/loc/%s/cache' % (pagename,)

		self.render('locality.html',
					user=self.user,
					locality=locality.get(),
					shop_results=shop_results,
					artist_results=artist_results,
					api_url=api_url)

class LocalityPageCache(BaseHandler):
	def get(self, pagename):
		# Set count and page
		count = self.request.get('count') and self.request.get('count') or 30
		page = self.request.get('page') and int(self.request.get('page')) or 1

		# Get slice of media list
		end = count * page
		start = end - count
		cached_ml = memcache.get('%s_recent_media' % (pagename,))

		if cached_ml and page * count - len(cached_ml) < count:
			media_list = cached_ml[start:end]

			# Convert media items to JSON
			media_list_dicts = []

			for media_item in media_list:
				mi_dict = helper.adjust_media_item(utils.to_dict(media_item))
				media_list_dicts.append(mi_dict)

			# Wrap in envelope
			api_url = 'http://%s/loc/%s/cache' % (socket.gethostname(), pagename,)
			max_id = media_list[-1].id

			# Is there a next page
			if not len(cached_ml) - (page + 1) * count > 0:
				page = -1 # No, final page
			output_json = helper.ig_envelope(media_list_dicts, api_url, page, max_id)
		else:
			output_json = {"meta":{"code":503}}

		# Output as JSON
		self.json_output(output_json)

class ContactPage(BaseHandler):
	def get(self, pagename):
		if not pagename:
			self.redirect('/shops-artists')
		else:
			max_id = self.request.get('max_id')

			info('pagename',pagename)

			contact_name, cid = pagename.split('/')
			contact_name = urllib.unquote_plus(contact_name)
			self.contact = helper.get_contact(self.contact_type, contact_name, cid)

			if not self.user:
				self.call_cached_page(pagename)
			else:
				# Logged in user			
				self.api_url = self.ig_user_media_recent(self.contact, self.user.access_token)

				if not self.api_url and self.contact_type == 'shop':
					self.api_url = self.ig_location_media_recent(self.contact, self.user.access_token)

	def call_cached_page(self, pagename):# Anonymous User
		self.media = memcache.get('Philadephia_recent_media')
		if self.media:
			self.media = self.media[:12] # only show 12 pics on anonymous screen

class ShopPage(ContactPage):
	def initialize(self, *a, **kw):
		BaseHandler.initialize(self, *a, **kw)
		self.contact_type = 'shop'

	def get(self, pagename):
		super(ShopPage, self).get(pagename)
				
		if self.user:
			self.render('shop.html',
						user=self.user,
						shop=self.contact,
						api_url=self.api_url)

	def call_cached_page(self, pagename):
		super(ShopPage, self).call_cached_page(pagename)

		self.render('shop_cached.html',
					user=self.user,
					shop=self.contact,
					media=self.media,
					next=None)

class ArtistPage(ContactPage):
	def initialize(self, *a, **kw):
		BaseHandler.initialize(self, *a, **kw)
		self.contact_type = 'artist'

	def get(self, pagename):
		super(ArtistPage, self).get(pagename)

		self.render('artist.html',
					user=self.user,
					artist=self.contact,
					api_url=self.api_url)

app = webapp2.WSGIApplication([('/?',Home),
							   ('/login', Login),
							   ('/logoff', Logoff),
							   ('/tattoos/?', Tattoos),
							   ('/tattoos/(.*)?', TattooCategoryPage),
							   ('/shops-artists', ShopsArtists),
							   ('/loc/(.*)/cache', LocalityPageCache),
							   ('/loc/?(.*)?', LocalityPage),
							   ('/shop/(.*)?', ShopPage),
							   ('/artist/(.*)?',ArtistPage),
							   ('/(.*)?', FourOhFour)], debug = True)