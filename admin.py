''' Admin Interface Handlers '''

# internal
from main import *
from google.appengine.datastore.datastore_query import Cursor

class AdminMain(BaseHandler):
	def get(self):
		self.render('admin_main.html',title='Main', active = 'admin')

class AdminModels(BaseHandler):
	def get(self):
		curs = Cursor(urlsafe = self.request.get('cursor'))
		studios, next_curs, more = Studio.query().order(-Studio.last_edited).fetch_page(10, start_cursor = curs)
		if studios:
			studios = [{'name':studio.name, 
						'last_edited':studio.last_edited, 
						'link':'/admin/models/studio/view%s' % (self.key_to_path(studio.key))} 
							for studio in studios]
			info("studios", studios)
			self.render('admin_models.html', title='Data Models', active = 'models', studios = studios, next_curs = next_curs.urlsafe(), more = more)
		else:
			self.render('admin_models.html', title='Data Models', active = 'models', studios = [], next_curs = '', more = '')

class AdminStudio(BaseHandler):
	def get(self, pagename):
		try:
			info(pagename)
			self.render('admin_studio_%s.html' % (pagename), active='models', active_nav = 'studio')
		except jinja2.TemplateNotFound:
			self.redirect('/admin/models')

class AdminCreate(BaseHandler):
	def get(self):
		self.render('admin_studio_create.html', active_nav = 'studio', args = {}, num_fields = {})

	def post(self):
		# Collect all POSTed arguments
		args = {arg:self.request.get(arg) for arg in self.request.arguments()}

		# multi_fields list contains all form fields that can be 1 or more
		multi_fields = ['email','phonenumber','country_code','phonetype','website','gallery','instagram_un','facebook_un','twitter_un','tumblr_un']
		
		# num_fields is a dict which counts the number of each multi_field; passed to template so that it outputs correct number of fields
		num_fields = {field:len([arg for arg in self.request.arguments() if arg.startswith(field)]) for field in multi_fields}
			
		try:
			# Validate form data before putting to DB
			error = ''
			raise_it = False

			# Name validation
			if not args.get('name'):
				error += 'Studio must have a name'
				raise_it = True

			# Validation functions
			validation_funcs = {'name':self.valid_name,
								'email':self.valid_email,
								'phonenumber':self.valid_phonenumber,
								'country_code':self.valid_country_code,
								'phonetype':self.valid_phonetype,
								'website':self.valid_url,
								'gallery':self.valid_url,
								'instagram_un':self.valid_instagram_un,
								'facebook_un':self.valid_facebook_un,
								'twitter_un':self.valid_twitter_un,
								'tumblr_un':self.valid_tumblr_un,
								'street':self.valid_street,
								'locality':self.valid_locality,
								'country':self.valid_country,
								'subdivision':self.valid_subdivision,
								'postal_code':self.valid_postal_code,
								'ma_toggle':self.valid_toggle,
								'ma_street':self.valid_street,
								'ma_locality':self.valid_locality,
								'ma_country':self.valid_country,
								'ma_subdivision':self.valid_subdivision,
								'ma_postal_code':self.valid_postal_code}

			# Traverse arguments
			for arg in args:
				if args.get(arg):
					# Handle multi_field args
					if arg in multi_fields:
						for i in range(1,num_fields[arg.split('-')[0]] + 1):
							ext = ''
							if i > 1: ext = '-%s' % (i,)

							if args.get('%s%s' % (arg,ext)) and not validation_funcs[arg.split('-')[0]](args.get('%s%s' % (arg,ext))):
								error += '%s field: "%s" is in a wrong format. Try again. # ' % (arg.capitalize(), args.get('%s%s' % (arg,ext)))
								raise_it = True

							# Special case to make sure all 3 phone fields are filled out
							if arg == ('phonenumber%s' % (ext)) and (not args['country_code%s' % (ext,)] or not args['phonetype%s' % (ext,)] or not args['phonenumber%s' % (ext,)]):
								error += 'Please fill in all three phone fields. #'
								raise_it = True
					# Single field args
					elif not validation_funcs[arg.split('-')[0]](args.get(arg)):
						error += '%s field: "%s" is in a wrong format. Try again. # ' % (arg, args[arg])
						raise_it = True

			if raise_it: raise Exception()

			# Put form fields into database
			new_studio = Studio(parent = ndb.Key('Country', args['country'], 'Subdivision', args['subdivision'], 'Locality', args['locality']),
								name = args['name'])
			new_studio.put()

			# Traverse arguments and put if exist
			for arg in args:
				if args.get(arg):
					primary = False
					ext = ''
					if len(arg.split('-')) <= 1: primary = True
					else: ext = '-%s' % (arg.split('-')[1])

					if arg.startswith('email'):
						Email(
							contact = new_studio.key,
							email = args[arg],
							primary = primary
							).put()
					elif arg.startswith('phonenumber'):
						Phone(
							contact = new_studio.key,
							phone_type = args['phonetype%s' % (ext,)],
							country_code = args['country_code%s' % (ext,)],
							number = args[arg],
							primary = primary
							).put()
					elif arg.startswith('website'):
						Website(
							contact = new_studio.key,
							url = args[arg],
							primary = primary
							).put()
					elif arg.startswith('gallery'):
						Gallery(
							contact = new_studio.key,
							url = args[arg],
							primary = primary
							).put()
					elif arg.startswith('instagram_un'):
						InstagramUsername(
							contact = new_studio.key,
							instagram_username = args[arg],
							primary = primary
							).put()
					elif arg.startswith('facebook_un'):
						FacebookUsername(
							contact = new_studio.key,
							facebook_username = args[arg],
							primary = primary
							).put()
					elif arg.startswith('twitter_un'):
						TwitterUsername(
							contact = new_studio.key,
							twitter_username = args[arg],
							primary = primary
							).put()
					elif arg.startswith('tumblr_un'):
						TumblrUsername(
							contact = new_studio.key,
							tumblr_username = args[arg],
							primary = primary
							).put()
					elif arg == 'country':
						Address(
							contact = new_studio.key,
							street = args['street'],
							locality = args['locality'],
							subdivision = args['subdivision'],
							country = args[arg],
							postal_code = args['postal_code']
							).put()
						Country(
							id = '%s' % (args[arg],),
							display_name = COUNTRIES[args[arg]]['name']
							).put()
						Subdivision(
							parent = ndb.Key('Country', args['country']),
							id = args['subdivision'],
							display_name = COUNTRIES[args[arg]]['subdivisions'][args['subdivision']]
							).put()
						Locality(
							parent = ndb.Key('Country', args['country'], 'Subdivision', args['subdivision']),
							id = args['locality'],
							display_name = args['locality']
							).put()
					elif arg == 'ma_country':
						MailingAddress(
							contact = new_studio.key,
							street = args['ma_street'],
							locality = args['ma_locality'],
							subdivision = args['ma_subdivision'],
							country = args[arg],
							postal_code = args['ma_postal_code']
							).put()

			self.redirect('/admin/models/studio/view%s' % (self.key_to_path(new_studio.key)))
		except:
			# Error, so re-render form with error message
			error += '%s: %s' % (sys.exc_info()[0], sys.exc_info()[1])

			self.render('admin_studio_create.html', active_nav = 'studio', args = args, num_fields = num_fields, error = error)

	def valid_name(self, name):
		NAME_RE = re.compile(r"^[!:.,'\sa-zA-Z0-9_-]{3,250}$")
		return NAME_RE.match(name)

	def valid_email(self, email):
		EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
		return EMAIL_RE.match(email)

	def valid_phonenumber(self, phonenumber):
		PHONENUMBER_RE = re.compile(r"^[0-9-\s()+]+$")
		return PHONENUMBER_RE.match(phonenumber)

	def valid_country_code(self, country_code):
		return int(country_code) in [1,49]

	def valid_phonetype(self, phonetype):
		return phonetype in ['home','work','fax','mobile','other']

	def valid_url(self, url):
		URL_RE = re.compile(r"^http+[!#$&-;=?-_a-z~]+\.+[!#$&-;=?-_a-z~]+$")
		return URL_RE.match(url)

	def valid_instagram_un(self, instagram_un):
		INSTAGRAM_UN_RE = re.compile(r"^[A-Za-z0-9_]{1,30}$")
		return INSTAGRAM_UN_RE.match(instagram_un)

	def valid_facebook_un(self, facebook_un):
		FACEBOOK_UN_RE = re.compile(r"^[a-z\d\.-]{5,50}$")
		return FACEBOOK_UN_RE.match(facebook_un)

	def valid_twitter_un(self, twitter_un):
		TWITTER_UN_RE = re.compile(r"^[A-Za-z0-9_]{1,32}$")
		return TWITTER_UN_RE.match(twitter_un)

	def valid_tumblr_un(self, tumblr_un):
		TUMBLR_UN_RE = re.compile(r"^[A-Za-z0-9-_]{1,32}$")
		return TUMBLR_UN_RE.match(tumblr_un)

	def valid_street(self, street):
		STREET_RE = re.compile(r"^.[\s#.,;:'()a-zA-Z0-9_-]+$")
		return STREET_RE.match(street)

	def valid_locality(self, locality):
		LOCALITY_RE = re.compile(r"^.[\s,.'()a-zA-Z-]+$")
		return LOCALITY_RE.match(locality)

	def valid_country(self, country):
		return country in ["AF","AX","AL","DZ","AS","AD","AO","AI","AQ","AG","AR","AM","AW","AU","AT","AZ","BS","BH","BD","BB","BY","BE","BZ","BJ","BM","BT","BO","BQ","BA","BW","BV","BR","IO","BN","BG","BF","BI","KH","CM","CA","CV","KY","CF","TD","CL","CN","CX","CC","CO","KM","CG","CD","CK","CR","CI","HR","CU","CW","CY","CZ","DK","DJ","DM","DO","EC","EG","SV","GQ","ER","EE","ET","FK","FO","FJ","FI","FR","GF","PF","TF","GA","GM","GE","DE","GH","GI","GR","GL","GD","GP","GU","GT","GG","GN","GW","GY","HT","HM","VA","HN","HK","HU","IS","IN","ID","IR","IQ","IE","IM","IL","IT","JM","JP","JE","JO","KZ","KE","KI","KP","KR","KW","KG","LA","LV","LB","LS","LR","LY","LI","LT","LU","MO","MK","MG","MW","MY","MV","ML","MT","MH","MQ","MR","MU","YT","MX","FM","MD","MC","MN","ME","MS","MA","MZ","MM","NA","NR","NP","NL","NC","NZ","NI","NE","NG","NU","NF","MP","NO","OM","PK","PW","PS","PA","PG","PY","PE","PH","PN","PL","PT","PR","QA","RE","RO","RU","RW","BL","SH","KN","LC","MF","PM","VC","WS","SM","ST","SA","SN","RS","SC","SL","SG","SX","SK","SI","SB","SO","ZA","GS","SS","ES","LK","SD","SR","SJ","SZ","SE","CH","SY","TW","TJ","TZ","TH","TL","TG","TK","TO","TT","TN","TR","TM","TC","TV","UG","UA","AE","GB","US","UM","UY","UZ","VU","VE","VN","VG","VI","WF","EH","YE","ZM","ZW"]

	def valid_subdivision(self, subdivision):
		return subdivision in ["US-AL","US-AK","US-AS","US-AZ","US-AR","US-CA","US-CO","US-CT","US-DE","US-DC","US-FL","US-GA","US-GU","US-HI","US-ID","US-IL","US-IN","US-IA","US-KS","US-KY","US-LA","US-ME","US-MD","US-MA","US-MI","US-MN","US-MS","US-MO","US-MT","US-NE","US-NV","US-NH","US-NJ","US-NM","US-NY","US-NC","US-ND","US-MP","US-OH","US-OK","US-OR","US-PA","US-PR","US-RI","US-SC","US-SD","US-TN","US-TX","US-UM","US-UT","US-VT","US-VI","US-VA","US-WA","US-WV","US-WI","US-WY","DE-BW","DE-BY","DE-BE","DE-BB","DE-HB","DE-HH","DE-HE","DE-MV","DE-NI","DE-NW","DE-RP","DE-SL","DE-SN","DE-ST","DE-SH","DE-TH"]

	def valid_postal_code(self, postal_code):
		POSTAL_CODE_RE = re.compile(r"^.[a-zA-Z0-9-\s]+$")
		return POSTAL_CODE_RE.match(postal_code)

	def valid_toggle(self, toggle):
		return toggle in ['yes','no']

class AdminView(BaseHandler):
	def get(self, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get studio
		studio = ancestor_key.get()

		# Exchange country and subdivision id names for more readable names (e.g. "Pennsylvania" instead of "US-PA")
		studio.country = COUNTRIES[studio.address.get().country]['name']
		studio.subdivision = COUNTRIES[studio.address.get().country]['subdivisions'][studio.address.get().subdivision]

		if studio.mailing_address.get():
			studio.ma_country = COUNTRIES[studio.mailing_address.get().country]['name']
			studio.ma_subdivision = COUNTRIES[studio.mailing_address.get().country]['subdivisions'][studio.mailing_address.get().subdivision]

		# Tag on the edit and delete links
		studio.edit = '/admin/models/studio/edit/%s' % (pagename,)
		studio.delete = '/admin/models/studio/delete/%s' % (pagename,)

		# Call the template
		self.render('admin_studio_view.html', active='models', active_nav = 'studio', studio = studio)

class AdminEdit(BaseHandler):
	def get(self, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get studio
		studio = ancestor_key.get()

class AdminDelete(BaseHandler):
	def get(self, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get studio
		studio = ancestor_key.get()
		studio.view = '/admin/models/studio/view/%s' % (pagename,)

		# Call the template
		self.render('admin_studio_delete.html', active='models', active_nave = 'studio', studio = studio)

	def post(self, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get studio
		name = ancestor_key.get().name

		# Call the template
		if self.request.get('delete') and self.request.get('delete') == 'yes':
			for prop_name,prop in ancestor_key.get().props.iteritems():
				try:
					ndb.delete_multi([p.key for p in prop.fetch()])
				except AttributeError:
					pass
			# Delete studio
			ancestor_key.delete()
			self.render('admin_studio_delete.html', active='models', active_nave = 'studio', name = name, confirmation = True)
		else:
			self.redirect('/admin/models/studio/delete/%s' % (pagename,))


app = webapp2.WSGIApplication([('/admin/?', AdminMain),
							   ('/admin/models', AdminModels),
							   ('/admin/models/studio/create/?', AdminCreate),
							   ('/admin/models/studio/view/([\+\s,.\'()0-9a-zA-Z\/_-]*?)', AdminView),
							   ('/admin/models/studio/edit/([\+\s,.\'()0-9a-zA-Z\/_-]*?)', AdminEdit),
							   ('/admin/models/studio/delete/([\+\s,.\'()0-9a-zA-Z\/_-]*?)', AdminDelete),
							   ('/admin/models/studio/([0-9a-zA-Z]*?)', AdminStudio)], debug=True)