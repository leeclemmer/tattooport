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
from collections import OrderedDict

# internal
import fix_path
import keys
import utils
import cache
import helper
from countries import COUNTRIES
from utils import info
from models import *
from config import *


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

	def ig_users_media_liked(self, access_token):
		return '%s%s' % ('https://api.instagram.com/v1/users/self/media/liked',
						self.ig_url_params(access_token))

	def json_output(self, *a, **kw):
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		if a: self.write(json.dumps(a[0], sort_keys=True, indent=4, separators=(',', ': ')))
		elif kw: self.write(json.dumps(kw))

	def popular_json(self, plid):
		# Get popular list ID
		plid = helper.plid(plid)

		# Get popular list for locality
		pop_list = helper.get_pop_list(plid)

		# Sort by date
		pop_list = sorted(pop_list, key=lambda x: x.created_time, reverse=True)

		# Convert list to dictionary
		pop_list = helper.media_list_to_json(pop_list)

		# Wrap in envelope
		pop_list = helper.ig_envelope(pop_list,
									  api_url='',
									  page=-1,
									  max_id='',
									  page_type='multi_user')

		self.json_output(pop_list)

	def get_localities(self):
		regions = regions_in_db()
		localities = []

		for country in regions:
			if country[0].key.id() == 'US':
				for subdivision in country[1]:
					for locality in subdivision[1]:
						if locality[0].display_name in FEATURED_CITIES:
							locality.append(self.key_to_path(locality[0].key))
							localities.append(locality)

		return sorted(localities,key=lambda x: x[0].display_name)

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
		# Set cache url as api_url
		api_url = '/json'

		self.render('home.html',
					user=self.user,
					api_url=api_url)

class HomePopularJson(BaseHandler):
	def get(self):
		self.popular_json('Frontpage')

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
											   access_token=access_token[0]
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
			self.redirect(authentication_url)
			'''self.render('login.html',
						 authentication_url=authentication_url)'''

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
		category_name_joined = ''.join(category_name.split(' '))
		category = ndb.Key('TattooGroup', parent, 
						   'TattooCategory', category_name_joined).get()

		if self.user:
			api_url = self.ig_tag_recent_media(category, self.user.access_token)
			
			self.render('tattoo_category.html',
					user=self.user,
					category=category,
					api_url=api_url)
		else: # Anonymous User
			self.media = memcache.get(category_name)
			if not self.media: # cold cache
				if cache.refresh_category(category_name):
					self.media = memcache.get(category_name)
			if self.media:
				self.media = self.media[:12] # only show 12 pics on anonymous screen

				self.render('tattoo_category_cached.html',
							user=self.user,
							category=category,
							media=self.media)

class ShopsArtists(BaseHandler):
	def get(self):
		self.render('shops_artists.html',
					user=self.user,
					localities=self.get_localities())

class LocalityPage(BaseHandler):
	def get(self, pagename):
		# Get Locality key
		if pagename.endswith('/'): pagename = pagename[:-1]
		locality = self.path_to_key(pagename.split('&')[0])
		
		# Prevent user from URL hacking
		if pagename.count('/') is not 2:
			self.redirect('/shops-artists')
		else:
			# Fetch shops
			shop_results = helper.nearby_shops(locality)
			shop_results = sorted(shop_results, key=lambda x: x.name)

			# Fetch artists
			artist_results = helper.shops_artists(shop_results)
			artist_results = sorted(artist_results, key=lambda x: x.display_name)
			
			# Add encoded name to shop list
			shop_results = zip(shop_results, [urllib.quote_plus(result.name) for result in shop_results ])

			# Add path to artist list
			artist_results = zip(artist_results,[urllib.quote_plus(result.display_name) for result in artist_results])

			# Set cache url as api_url
			api_url = '/loc/%s/json' % (pagename,)

			self.render('locality.html',
						user=self.user,
						locality=locality.get(),
						shop_results=shop_results,
						artist_results=artist_results,
						api_url=api_url)

class LocalityPopularJson(BaseHandler):
	def get(self, pagename):
		# Unquote the pagename
		pagename = urllib.unquote_plus(pagename)

		self.popular_json(pagename)

class LocalityAllContacts(BaseHandler):
	def get(self, pagename, contact_type):
		locality = self.path_to_key(pagename)

		# Fetch shops
		shop_results = helper.nearby_shops(locality)
		shop_results = sorted(shop_results, key=lambda x: x.name)

		if contact_type == 'artists':
			# Fetch artists
			artist_results = helper.shops_artists(shop_results)
			artist_results = sorted(artist_results, key=lambda x: x.display_name)
			
			# Add path to artist list
			artist_results = zip(artist_results,[urllib.quote_plus(result.display_name) for result in artist_results])

			self.render('locality-artists.html',
						user=self.user,
						locality=locality.get(),
						artist_results=artist_results)
			
		elif contact_type == 'shops':
			# Add encoded name to shop list
			shop_results = zip(shop_results, [urllib.quote_plus(result.name) for result in shop_results ])

			self.render('locality-shops.html',
						user=self.user,
						locality=locality.get(),
						shop_results=shop_results)

class ContactPage(BaseHandler):
	''' Parent class handler for Shop and Artist. '''

	def get(self, pagename):
		if not pagename:
			self.redirect('/shops-artists')
		else:
			max_id = self.request.get('max_id')

			if pagename.count('/') > 1:
				pagename = '/'.join(pagename.split('/')[:2])

			contact_name, cid = pagename.split('/')
			contact_name = urllib.unquote_plus(contact_name)
			self.contact = helper.get_contact(self.contact_type, contact_name, cid)

			if self.user:
				# Logged in user			
				self.api_url = self.ig_user_media_recent(self.contact, 
					self.user.access_token)

				if not self.api_url and self.contact_type == 'shop':
					# Set api_url to fetch location media 
					# instead of IG user account
					self.api_url = self.ig_location_media_recent(
						self.contact, self.user.access_token)
			elif not self.user:
				# Anonymous user; setting api_url to json page
				self.api_url = 'http://%s/%s/%s/json' % (socket.gethostname(), 
														 self.contact_type,
														 pagename)

	def get_media(self, pagename):
		''' Retrieves media for contact page.
			If it can't find it in memcache, it sets memcache.
		'''
		self.media = memcache.get(pagename)

		if not self.media: # cold cache
			self.media = cache.refresh_contact(pagename, self.contact_type)
			memcache.set(pagename, self.media)

		if self.media:
			self.media = self.media[:ANONYMOUS_PHOTO_COUNT]

class ContactPageJson(ContactPage):
	''' Provides JSON interface to media list of contact.
		Called for anonymous user.
	'''

	def get(self, contact_type, pagename):
		self.contact_type = contact_type

		# Get media list
		self.get_media(pagename)
		if self.media != 'NOFEED':
			media_list_dicts = helper.media_list_to_json(self.media)
		else:
			media_list_dicts = helper.media_list_to_json([])


		# Output json
		self.json_output(helper.ig_envelope(media_list_dicts))

class ContactRedirect(BaseHandler):
	def get(self, ig_username):
		contact = Contact.by_ig_username(ig_username)
		if contact:
			contact = contact.get()
			contact_type = contact.class_[1]

			if contact_type == 'Studio':
				contact_type = 'shop'
				name = urllib.quote_plus(contact.name)
			elif contact_type == 'Artist':
				contact_type = 'artist'
				name = urllib.quote_plus(contact.display_name)
			
			path = '/%s/%s/%s' % (contact_type, name, contact.key.id())
			self.redirect(path)
		else:
			error_msg = '''<h3><a href="https://instagram.com/%s" target="_blank">
				Try on Instagram?</a></h3>''' % (ig_username)

			title = 'Couldn\'t find %s on TattooPort :(' % (ig_username,)

			self.render('error.html',
						  title=title,
						  error_message=error_msg)

class ShopPage(ContactPage):
	def initialize(self, *a, **kw):
		BaseHandler.initialize(self, *a, **kw)
		self.contact_type = 'shop'

	def get(self, pagename):
		super(ShopPage, self).get(pagename)

		# Exchange country and subdivision id names for more readable names (e.g. "Pennsylvania" instead of "US-PA")
		try:
			self.contact.country = COUNTRIES[self.contact.address.get().country]['name']
			self.contact.subdivision = COUNTRIES[self.contact.address.get().country]['subdivisions'][self.contact.address.get().subdivision]
		except:
			pass
				
		self.render('shop.html',
					user=self.user,
					shop=self.contact,
					featured_cities=FEATURED_CITIES,
					api_url=self.api_url)

class ArtistPage(ContactPage):
	def initialize(self, *a, **kw):
		BaseHandler.initialize(self, *a, **kw)
		self.contact_type = 'artist'

	def get(self, pagename):
		super(ArtistPage, self).get(pagename)

		#cache.update_popular_list('US/US-PA/Philadelphia',pagename, 'artist')

		self.render('artist.html',
				user=self.user,
				artist=self.contact,
				featured_cities=FEATURED_CITIES,
				api_url=self.api_url)

class MyLikes(BaseHandler):
	def get(self):
		if not self.user:
			self.redirect('/')
		else:
			api_url = self.ig_users_media_liked(self.user.access_token)
			self.render('my_likes.html',
						user=self.user,
						api_url=api_url)

class IGMediaLike(BaseHandler):
	def get(self, like, media_id):
		if not media_id or not self.user:
			self.redirect('/')
		else:
			api = helper.get_instagram_api(access_token=self.user.access_token)
			try:				
				if like == 'like':
					api.like_media(media_id)
				elif like == 'unlike':
					api.unlike_media(media_id)
				self.json_output({"meta":{"code": 200},"data": None})
			except:
				utils.catch_exception()
				self.json_output({"meta":{"code": 400},"data": None})

class IGUserFollow(BaseHandler):
	def get(self, follow, user_id):
		if not user_id or not self.user:
			self.redirect('/')
		else:
			api = helper.get_instagram_api(access_token=self.user.access_token)
			try:				
				if follow == 'follow':
					api.follow_user(user_id=user_id)
				elif follow == 'unfollow':
					api.unfollow_user(user_id=user_id)
				self.json_output({"meta":{"code": 200},"data": None})
			except:
				utils.catch_exception()
				self.json_output({"meta":{"code": 400},"data": None})

class Sitemap(BaseHandler):
	''' Outputs sitemaps.org compliant Sitemap for Google Webmasters.'''
	def get(self):
		host = 'http://www.tattooport.com'
		if os.environ['SERVER_NAME'] == 'localhost':
			host = 'http://localhost:16080'

		self.response.headers['Content-Type'] = 'application/xml'
		self.response.write('<?xml version="1.0" encoding="UTF-8"?>')
		self.response.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

		# Home
		self.url_wrap(host, '1')

		# Localities
		localities = locality_keys_in_db()

		for locality in localities:
			lp = locality.pairs()
			if lp[-1][1] in FEATURED_CITIES:
				self.url_wrap('%s/loc/%s/%s/%s' % (host, lp[0][1], 
					lp[1][1], lp[2][1]), '0.9')
				self.url_wrap('%s/loc/%s/%s/%s/artists' % (host, lp[0][1], 
					lp[1][1], lp[2][1]), '0.8')
				self.url_wrap('%s/loc/%s/%s/%s/shops' % (host, lp[0][1], 
					lp[1][1], lp[2][1]), '0.8')

		# Studios
		studio_cache_ids = StringList.get_by_id('StudioCacheIds').string_list

		for scid in studio_cache_ids:
			self.url_wrap('%s/shop/%s' % (host, scid), '0.8')

		# Artists
		artist_cache_ids = StringList.get_by_id('ArtistCacheIds').string_list

		for scid in artist_cache_ids:
			self.url_wrap('%s/artist/%s' % (host, scid), '0.8')

		# Categories
		groups = TattooGroup.all_groups()
		for group in groups:
			for category in group[1]:
				self.url_wrap('%s/tattoos/%s/%s' % (host,
					group[0].name,category.name), '0.8')

		# Static Pages
		self.url_wrap('%s/about' % (host,), '0.5')

		self.response.write('</urlset>')

	def url_wrap(self, url, prio):
		self.response.write('<url>')

		self.response.write('<loc>')
		self.response.write(url)
		self.response.write('</loc>\n')

		self.response.write('<changefreq>')
		self.response.write('daily')
		self.response.write('</changefreq>\n')

		self.response.write('<priority>')
		self.response.write(prio)
		self.response.write('</priority>\n')
		self.response.write('</url>\n\n')


# Static Pages

class About(BaseHandler):
	def get(self):
		self.render('about.html',
					user=self.user)

class TermsOfService(BaseHandler):
	def get(self):
		self.render('tos.html',
					user=self.user)

class PrivacyPolicy(BaseHandler):
	def get(self):
		self.render('pp.html',
					user=self.user)

app = webapp2.WSGIApplication([('/?',Home),
							   ('/json',HomePopularJson),
							   ('/login', Login),
							   ('/logoff', Logoff),
							   ('/tattoos/?', Tattoos),
							   ('/tattoos/(.*)?', TattooCategoryPage),
							   ('/shops-artists', ShopsArtists),
							   ('/loc/(.*)/json', LocalityPopularJson),							   
							   ('/loc/(.*)/(shops|artists)/?', LocalityAllContacts),
							   ('/loc/?(.*)?', LocalityPage),
							   ('/(shop|artist)/(.*)/json', ContactPageJson),
							   ('/shop/(.*)?', ShopPage),
							   ('/artist/(.*)?', ArtistPage),
							   ('/i/(.*)/?', ContactRedirect),
							   ('/my/likes/?', MyLikes),
							   ('/igm/(like|unlike)/(.*)/?', IGMediaLike),
							   ('/igu/(follow|unfollow)/(.*)/?', IGUserFollow),
							   ('/sitemap', Sitemap),
							   ('/about', About),
							   ('/tos', TermsOfService),
							   ('/pp', PrivacyPolicy),
							   ('/(.*)?', FourOhFour)], debug = True)