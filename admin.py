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
			self.render('admin_studio_%s.html' % (pagename), active_nav = 'studio', args = {}, num_fields = {})
		except jinja2.TemplateNotFound:
			self.redirect('/admin/models')

	def post(self, pagename):
		if pagename == 'create':
			# Collect all POSTed arguments
			args = {arg:self.request.get(arg) for arg in self.request.arguments()}

			# multi_fields list contains all form fields that can be 1 or more
			multi_fields = ['email','phonenumber','website','gallery','instagram_username','facebook_username','twitter_username','tumblr_username']

			try:
				# Put form fields into database
				print e[1]
			except:
				# Error, so re-render form with error message
				e = sys.exc_info()[1]

				# num_fields is a dict which counts the number of each multi_field; passed to template so that it outputs correct number of fields
				num_fields = {field:len([arg for arg in self.request.arguments() if arg.startswith(field)]) for field in multi_fields}
				
				self.render('admin_studio_create.html', active_nav = 'studio', args = args, num_fields = num_fields, error = e)


app = webapp2.WSGIApplication([('/admin/?', AdminMain),
							   ('/admin/models', AdminModels),
							   ('/admin/models/studio/([0-9a-zA-Z]*?)', AdminStudio)], debug=True)