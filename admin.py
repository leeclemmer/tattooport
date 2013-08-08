''' Admin Interface Handlers '''

# internal
from main import *

class AdminMain(BaseHandler):
	def get(self):
		self.render('admin_main.html',title='Main', active = 'admin')

class AdminModels(BaseHandler):
	def get(self):
		self.render('admin_models.html', title='Data Models', active = 'models')

app = webapp2.WSGIApplication([('/admin/?', AdminMain),
							   ('/admin/models', AdminModels)], debug=True)