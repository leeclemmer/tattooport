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

class AdminPopularCities(BaseHandler):
	def get(self):
		# Get list of cities from Localities list
		cities = KeyList.get_by_id('Localities').key_list

		# Construct parent path strings
		cities = sorted([city_key.pairs()[0][1] + '/' + \
				  city_key.pairs()[1][1] + '/' + \
				  city_key.pairs()[2][1] for city_key in cities])

		# Remove non-featured cities
		cities = [city for city in cities \
				  if city.rsplit('/',1)[1] in FEATURED_CITIES]

		self.render('admin_popular_cities.html', 
					title='Pick a City',
					active='content',
					cities=cities
					)

class AdminPopularPage(BaseHandler):
	def set_vars(self, city):		
		if city != 'frontpage':
			self.city = city.rsplit('/',1)[0].upper() + '/' + \
			   	   city.rsplit('/',1)[1].title()
		elif city == 'frontpage':
			self.city = 'Frontpage'

		# Get popular list ID
		self.plid = helper.plid('%s' % (self.city,))

		# Get popular list
		self.pop_list = helper.get_pop_list(self.plid)
		self.pop_list = sorted(self.pop_list, key=lambda x: x.created_time, reverse=True)

		info('self.pop_list', self.pop_list)

	def get(self, city):
		self.set_vars(city)

		info('self.pop_list', self.pop_list)

		self.render('admin_popular_page.html', 
					title=self.city,
					active='content',
					city=self.city,
					pop_list=self.pop_list				
					)

	def post(self, city):
		self.set_vars(city)

		# Get user ID to identify which pic to delete
		userid = self.request.get('userid')

		# Go through pop_list and remove user's pic
		for pop_item in self.pop_list:
			if pop_item.user.id == userid:
				del self.pop_list[self.pop_list.index(pop_item)]

		# Update list in DB and memcache
		PopularList.put_pop_list(self.plid, self.pop_list)
		memcache.set(self.plid, self.pop_list, time=60*60*2)

		msg = "Item deleted."

		self.render('admin_popular_page.html', 
					title=self.city,
					active='content',
					city=self.city,
					pop_list=self.pop_list,
					msg=msg					
					)


app = webapp2.WSGIApplication([('/admin/content/?', AdminContent),
							   ('/admin/content/popular/cities/?', AdminPopularCities),
							   ('/admin/content/popular/(.*)/?', AdminPopularPage)
							  ], debug=True)