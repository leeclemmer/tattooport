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

class Welcome(BaseHandler):
	def get(self):
		self.render('main_page.html', title = 'yup')

class MainPage(BaseHandler):
	def get(self):
		self.render('main_page.html')

app = webapp2.WSGIApplication([('/welcome', Welcome),
							   ('/.*', MainPage)], debug = True)