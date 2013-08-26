# builtins
import re
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'lib'))

import urllib
import urllib2
import json
import logging

# internal
import keys
import utils
from countries import COUNTRIES
from utils import info
from models import *

# external
import webapp2
import jinja2
from geopy import geocoders


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   extensions = ['jinja2.ext.loopcontrols'],
							   autoescape = True)

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
		''' Returns dictionary of how many Contact.prop_names in args there are for each arg. '''		
		# num_fields is a dict which counts the number of each Contact.prop_name; passed to template so that it outputs correct number of fields
		return {field:len([arg for arg in args if arg.startswith(field)]) for field in Contact.prop_names()}

	def geo_pt(self, address):
		''' Returns ndb.GeoPt for given address.'''
		g = geocoders.GoogleV3()
		try:
			geocodes = g.geocode(address,exactly_one=False)
			return ndb.GeoPt(geocodes[0][1][0],geocodes[0][1][1])
		except:
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
		

class Welcome(BaseHandler):
	def get(self):
		self.render('main_page.html', title = 'yup')

class MainPage(BaseHandler):
	def get(self):
		self.render('main_page.html')

app = webapp2.WSGIApplication([('/welcome', Welcome),
							   ('/.*', MainPage)], debug = True)