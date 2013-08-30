#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Admin Setting Interface Handlers '''

from main import *

class AdminSettings(BaseHandler):
	def get(self):
		self.render('admin_settings.html', 
					title='Settings',
					active='settings'
					)

class AdminStatsCounters(BaseHandler):
	def get(self):
		self.render('admin_stats_counters.html',
					title='Counters',
					active='settings',
					counters=self.counters()
					)

	def post(self):
		delete = self.request.get('delete')
		counter = self.request.get('counter')
		if delete == 'yes':
			general_counter.delete_counter(counter)
			self.redirect('/admin/settings/stats/counters')
		else:
			counters = self.request.get('counters')
			plusorminus = self.request.get('plusorminus')
			if plusorminus == 'plus':
				general_counter.increment(counter)
			elif plusorminus == 'minus':
				general_counter.decrement(counter)

			self.render('admin_stats_counters.html',
						title='Counters',
						active='settings',
						counters=self.counters(),
						counter=counter
						)

	def counters(self):
		''' Returns all available counters. '''
		counters = general_counter.GeneralCounterShardConfig.query().fetch()
		counters = sorted([counter.key.id() for counter in counters])
		counters = zip(counters, [general_counter.get_count(counter) for counter in counters])
		return counters


class AdminRegionsDelete(BaseHandler):
	def get(self):
		region = self.request.get('region')
		region_count_stu = ''
		region_count_art = ''
		region_name = ''

		if region:
			region_key = self.path_to_key(region)
			region_name = region_key.id()
			region_count_art = general_counter.get_count('%s Artist' % (region_name,))
			region_count_stu = general_counter.get_count('%s Studio' % (region_name,))

		self.render('admin_regions_delete.html',
					title='Delete Regions',
					active='settings',
					regions=self.regions_in_db(),
					region=region,
					region_name=region_name,
					region_count_art=region_count_art,
					region_count_stu=region_count_stu
					)
	
	def post(self):
		delete = self.request.get('delete')
		region = self.request.get('region')

		if region and delete == 'yes':
			region_key = self.path_to_key(region)
			region_name = region_key.id()
			general_counter.delete_counter('%s Artist' % (region_name,))
			general_counter.delete_counter('%s Studio' % (region_name,))
			region_key.delete()
			self.redirect('/admin/settings/regions/delete')


app = webapp2.WSGIApplication(
	[('/admin/settings/?', AdminSettings),
	 ('/admin/settings/stats/counters/?', AdminStatsCounters),
	 ('/admin/settings/regions/delete/?', AdminRegionsDelete)], debug=True)