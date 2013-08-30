#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Admin Interface Handlers '''

from main import *

class AdminMain(BaseHandler):
	def get(self):
		studio_count = general_counter.get_count('Studio')
		artist_count = general_counter.get_count('Artist')
		country_count = general_counter.get_count('Country')
		subd_count = general_counter.get_count('Subdivision')
		loca_count = general_counter.get_count('Locality')

		self.render('admin_main.html', 
					title='Main',
					active='admin',
					studio_count=studio_count,
					artist_count=artist_count,
					country_count=country_count,
					subd_count=subd_count,
					loca_count=loca_count
					)

app = webapp2.WSGIApplication(
	[('/admin/?', AdminMain)], debug=True)