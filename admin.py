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
	def get(self, name):
		info('name',name)
		try:
			self.render('admin_studio_%s.html' % (name), active_nav = 'studio')
		except jinja2.TemplateNotFound:
			self.redirect('/admin/models')

	def post(self, name):
		if name == 'create':
			phone = self.request.get('phone')
			info('phone', phone)


app = webapp2.WSGIApplication([('/admin/?', AdminMain),
							   ('/admin/models', AdminModels),
							   ('/admin/models/studio/([0-9a-zA-Z]*?)', AdminStudio)], debug=True)