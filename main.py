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

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   extensions = ['jinja2.ext.loopcontrols'],
							   autoescape = True)

class BaseHandler(webapp2.RequestHandler):	
	# multi_fields list contains all form fields that can be 1 or more
	multi_fields = ['email','phone_number','country_code','phone_type','website','gallery','instagram_un','facebook_un','twitter_un','tumblr_un']

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
		return '/%s/%s' % ('/'.join([urllib.quote_plus(pair[1]) for pair in key.pairs() if pair[0] == 'Country' or pair[0] == 'Subdivision' or pair[0] == 'Locality']),key.id())

	def path_to_key(self, path):
		''' Converts path to key with ancestor path. '''
		country, subdivision, locality, sid = urllib.unquote_plus(path).split('/')
		return ndb.Key('Country',country,'Subdivision',subdivision,'Locality',locality,'Contact',int(sid))

	def num_fields(self, args):
		''' Returns dictionary of how many multi_fields in args there are for each arg. '''		
		# num_fields is a dict which counts the number of each multi_field; passed to template so that it outputs correct number of fields
		return {field:len([arg for arg in args if arg.startswith(field)]) for field in self.multi_fields}			
		

class Welcome(BaseHandler):
	def get(self):
		self.render('main_page.html', title = 'yup')

class MainPage(BaseHandler):
	def get(self):
		self.render('main_page.html')

app = webapp2.WSGIApplication([('/welcome', Welcome),
							   ('/.*', MainPage)], debug = True)