import sys
import logging
import urllib
import urllib2
import json
from lxml import etree

class GGeocode():
	""" Wrapper for Google Geocode API v3.
	https://developers.google.com/maps/documentation/geocoding/
	"""
	def __init__(self, method='http',
					   output='json',
					   sensor='false',
					   address='',
					   components='',
					   latlng='',
					   client='',
					   signature='',
					   bounds='',
					   language='',
					   region=''):
		# Construct base url
		self.method = method.lower()
		if method not in ['http','https']:
			raise ValueError("""'method' is '%s' - 
				needs to be either 'http' or 'https'""" % (method,))

		self.output = output.lower()
		if output not in ['json','xml']:
			raise ValueError("""'output' is '%s' -
				needs to be either 'xml' or 'json'""" % (output,))

		self.base_url = '%s://maps.googleapis.com/maps/api/geocode/%s?' % \
			(method, output)

		# Collect parameters
		self.params = {}

		# required parameters:
		#	sensor
		#	address or latlng or components
		self.params['sensor'] = sensor.lower()
		if sensor not in ['true','false']:
			raise ValueError("""'sensor' is '%s' - 
				needs to be either 'true' or 'false'""" % (sensor,))

		if (address and (latlng or components)) or (latlng and components):
			raise ValueError("""Only supply one of these (not more): 
				address, latlng, or components""")

		if not address and not latlng and not components:
			raise ValueError("""Must supply one of the following:
				address, latlng, or components""")

		if address: self.params['address'] = address
		if latlng: self.params['latlng'] = latlng
		if components: 
			for component in components.split('|'):
				if ':' not in component:
					raise ValueError("""Component is %s - must be in the form 
						of 'component:value'""" % (component,))

				if component.split(':')[0] not in ['route',
												   'locality',
												   'administrative_area',
												   'postal_code',
												   'country']:
					 raise ValueError("""Component is %s - must be:
					 	route, locality, administrative_area, 
					 	postal_code or country""" % (component.split(':')[0],))
			self.params['components'] = components

		# optional parameters:
		#	client and signature
		#	bounds
		#	language
		#	region
		if (client and not signature) or (signature and not client):
			raise ValueError("""Must supply both client and signature.""")

		if client and signature:
			self.params['client'] = client
			self.params['signature'] = signature

		if bounds: self.params['bounds'] = bounds

		if language: self.params['language'] = language

		# Access Google Geocoder API
		try:
			self.url = '%s%s' % (self.base_url,
								 urllib.urlencode(self.params))
			self.response = urllib2.urlopen(self.url).read()
		except:
			e = sys.exc_info()[1]
			logging.error(e)

		# Get status and results
		if output == 'json':
			self.output = json.loads(self.response)
			self.status = self.output['status']
			self.results = self.output['results']
			self.results_count = len(self.results)
			if address or components:
				self.lat = self.results[0]['geometry']['location']['lat']
				self.lon = self.results[0]['geometry']['location']['lng']
			elif latlng:
				self.address = self.results[0]['formatted_address']
		elif output == 'xml':
			self.output = etree.fromstring(self.response)
			self.status = self.output.xpath('/GeocodeResponse/status/text()')[0]
			self.results = self.output.xpath('/GeocodeResponse/result')
			self.results_count = len(self.results)
			if address or components:
				self.lat = self.results[0].xpath('geometry/location/lat/text()')[0]			
				self.lon = self.results[0].xpath('geometry/location/lng/text()')[0]
			elif latlng:
				self.address = self.results[0].xpath('formatted_address')[0]


		if self.status != 'OK':
			logging.error("Call to %s unsuccessful (Error code '%s')" % \
				(self.url,self.status))