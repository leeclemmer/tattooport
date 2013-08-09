''' Admin Interface Handlers '''

# internal
from main import *

class AdminMain(BaseHandler):
	def get(self):
		self.render('admin_main.html',title='Main', active = 'admin')

class AdminModels(BaseHandler):
	def get(self):
		self.render('admin_models.html', title='Data Models', active = 'models')

class AdminStudio(BaseHandler):
	def get(self, pagename):
		try:
			self.render('admin_studio_%s.html' % (pagename), active_nav = 'studio')
		except jinja2.TemplateNotFound:
			self.redirect('/admin/models')

	def post(self, pagename):
		if pagename == 'create':
			# Init vars
			name = ''
			emails = []
			phones = []
			websites = []

			instagrams = []
			facebooks = []
			twitters = []
			tumblrs = []

			street = ''
			city = ''
			country = ''
			subdivision = ''
			postal_code = ''

			ma_street = ''
			ma_city = ''
			ma_country = ''
			ma_subdivision = ''
			ma_postal_code = ''

			for arg in self.request.arguments():
				# Set index insert into correct spot in list
				i = arg.split('-')
				if len(i) == 1: i = 0
				else: i = int(i[1])-1

				if arg == 'name': name = self.request.get(arg)
				elif 'email' in arg:  emails.insert(i,self.request.get(arg))
				elif 'phonenumber' in arg:
					if i == 0: pi = ''
					else: pi = '-' + str(i + 1)
					info('i, pi',i,pi)
					phones.insert(i,{'phonetype':self.request.get('phonetype%s' % (pi)),
								   'countrycode':self.request.get('countrycode%s' %(pi)),
								   'phonenumber':utils.numbers_only(self.request.get(arg))})
				elif 'website' in arg:  websites.insert(i,self.request.get(arg))

				elif 'instagram' in arg:  instagrams.insert(i,self.request.get(arg))
				elif 'facebook' in arg:  facebooks.insert(i,self.request.get(arg))
				elif 'twitter' in arg:  twitters.insert(i,self.request.get(arg))
				elif 'tumblr' in arg:  tumblrs.insert(i,self.request.get(arg))

				elif arg == 'street':  street = self.request.get(arg)
				elif arg == 'city':  city = self.request.get(arg)
				elif arg == 'country':  country = self.request.get(arg)
				elif arg == 'subdivision':  subdivision = self.request.get(arg)
				elif arg == 'postal_code': postal_code = self.request.get(arg)
				
				elif arg == 'ma_street':  ma_street = self.request.get(arg)
				elif arg == 'ma_city':  ma_city = self.request.get(arg)
				elif arg == 'ma_country':  ma_country = self.request.get(arg)
				elif arg == 'ma_subdivision':  ma_subdivision = self.request.get(arg)
				elif arg == 'ma_postal_code': ma_postal_code = self.request.get(arg)
			

			info('name',name)
			info('emails', emails)
			info('phones', phones)
			info('websites', websites)

			info('instagrams', instagrams)
			info('facebooks', facebooks)
			info('twitters', twitters)
			info('tumblrs', tumblrs)

			info('street', street)
			info('city', city)
			info('country', country)
			info('subdivision', subdivision)
			info('postal_code', postal_code)

			info('ma_street', ma_street)
			info('ma_city', ma_city)
			info('ma_country', ma_country)
			info('ma_subdivision', ma_subdivision)
			info('ma_postal_code', ma_postal_code)

			info('all args',self.request.arguments())


app = webapp2.WSGIApplication([('/admin/?', AdminMain),
							   ('/admin/models', AdminModels),
							   ('/admin/models/studio/([0-9a-zA-Z]*?)', AdminStudio)], debug=True)