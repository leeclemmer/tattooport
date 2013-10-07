#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Admin Setting Interface Handlers '''

from main import *

class AdminContent(BaseHandler):
	def get(self):
		self.render('admin_content.html', 
					title='Content',
					active='content'
					)

class AdminPopularFrontpage(BaseHandler):
	def get(self):
		self.render('admin_popular_frontpage.html', 
					title='Popular Frontpage',
					active='content'
					)

class AdminPopularCities(BaseHandler):
	def get(self):
		self.render('admin_popular_cities.html', 
					title='Pick a City',
					active='content'
					)

class AdminPopularCity(BaseHandler):
	def get(self, city):
		self.render('admin_popular_city.html', 
					title='Pick a City',
					active='content',
					city=city
					)

app = webapp2.WSGIApplication([('/admin/content/?', AdminContent),
							   ('/admin/content/popular/frontpage/?', AdminPopularFrontpage),
							   ('/admin/content/popular/cities/?', AdminPopularCities),
							   ('/admin/content/popular/(.*)/?', AdminPopularCity)
							  ], debug=True)