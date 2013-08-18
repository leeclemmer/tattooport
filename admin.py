#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Admin Interface Handlers '''

# internal
from main import *
from google.appengine.datastore.datastore_query import Cursor

class ValidationError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

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
			self.render('admin_models.html', title='Data Models', active = 'models', studios = studios, next_curs = next_curs.urlsafe(), more = more)
		else:
			self.render('admin_models.html', title='Data Models', active = 'models', studios = [], next_curs = '', more = '')

class AdminStudio(BaseHandler):
	def get(self, pagename):
		try:
			self.render('admin_studio_%s.html' % (pagename), active='models', active_nav = 'studio')
		except jinja2.TemplateNotFound:
			self.redirect('/admin/models')

	def valid_name(self, name):
		NAME_RE = re.compile(r"^[!:.,'\sa-zA-Z0-9_-]{3,250}$")
		return NAME_RE.match(name)

	def valid_email(self, email):
		EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
		return EMAIL_RE.match(email)

	def valid_phone_number(self, phone_number):
		PHONE_NUMBER_RE = re.compile(r"^[0-9-\s()+]+$")
		return PHONE_NUMBER_RE.match(phone_number)

	def valid_country_code(self, country_code):
		return int(country_code) in [1,49]

	def valid_phone_type(self, phone_type):
		return phone_type in ['home','work','fax','mobile','other']

	def valid_url(self, url):
		URL_RE = re.compile(r"^http+[!#$&-;=?-_a-z~]+\.+[!#$&-;=?-_a-z~]+$")
		return URL_RE.match(url)

	def valid_instagram(self, instagram):
		INSTAGRAM_RE = re.compile(r"^[A-Za-z0-9_]{1,30}$")
		return INSTAGRAM_RE.match(instagram)

	def valid_facebook(self, facebook):
		FACEBOOK_RE = re.compile(r"^[a-z\d\.-]{5,50}$")
		return FACEBOOK_RE.match(facebook)

	def valid_twitter(self, twitter):
		TWITTER_RE = re.compile(r"^[A-Za-z0-9_]{1,32}$")
		return TWITTER_RE.match(twitter)

	def valid_tumblr(self, tumblr):
		TUMBLR_RE = re.compile(r"^[A-Za-z0-9-_]{1,32}$")
		return TUMBLR_RE.match(tumblr)

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

	def validate_args(self, args):
		''' Takes list of args and validates them against validation rules.
			Returns (True/False, error)'''
		error = ''
		raise_it = False

		# Name validation
		if not args.get('name'):
			error += 'Studio must have a name'
			raise_it = True# Traverse arguments and run against validation function

		for arg in args:
			if args.get(arg):
				# Handle multi_field args
				if arg.split('-')[0] in Contact.prop_names() or arg.split('-')[0] in ['phone_number','phone_type','country_code']:
					if not self.validation_funcs[arg.split('-')[0]](self, args[arg]):
						error += '%s field: "%s" is in a wrong format. Try again. # ' % (arg.capitalize(), args[arg])
						raise_it = True

					# Special case to make sure all 3 phone fields are filled out
					ext = ''
					if len(arg.split('-')) > 1: ext = '-%s' % (arg.split('-',1)[1],)
					if arg.startswith('phone_number') and (not args['country_code%s' % (ext,)] or not args['phone_type%s' % (ext,)] or not args['phone_number%s' % (ext,)]):
						error += 'Please fill in all three phone fields. #'
						raise_it = True
				# Single field args
				elif arg != 'skey' and not self.validation_funcs[arg.split('-')[0]](self, args.get(arg)):
					error += '%s field: "%s" is in a wrong format. Try again. # ' % (arg, args[arg])
					raise_it = True

		return (raise_it,error)

	# Validation functions
	validation_funcs = {'name':valid_name,
						'email':valid_email,
						'phone_number':valid_phone_number,
						'country_code':valid_country_code,
						'phone_type':valid_phone_type,
						'website':valid_url,
						'gallery':valid_url,
						'instagram':valid_instagram,
						'foursquare':valid_url,
						'twitter':valid_twitter,
						'facebook':valid_url,
						'tumblr':valid_url,
						'street':valid_street,
						'locality':valid_locality,
						'country':valid_country,
						'subdivision':valid_subdivision,
						'postal_code':valid_postal_code,
						'ma_toggle':valid_toggle,
						'ma_street':valid_street,
						'ma_locality':valid_locality,
						'ma_country':valid_country,
						'ma_subdivision':valid_subdivision,
						'ma_postal_code':valid_postal_code}

class AdminCreate(AdminStudio):
	def get(self):
		self.render('admin_studio_create.html', active_nav = 'studio', args = {}, num_fields = {})

	def post(self):
		# Collect all POSTed arguments
		args = {arg:self.request.get(arg) for arg in self.request.arguments()}
			
		try:
			raise_it, error = self.validate_args(args)

			# if any of the fields failed validation
			if raise_it: raise ValidationError(error)

			# Put form fields into database
			if args.get('skey'):
				new_studio = self.path_to_key(args['skey']).get()
				new_studio.name = args['name']
			else:
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
					elif arg.startswith('phone_number'):
						Phone(
							contact = new_studio.key,
							phone_type = args['phone_type%s' % (ext,)],
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
					elif arg.startswith('instagram'):
						Instagram(
							contact = new_studio.key,
							instagram = args[arg],
							primary = primary
							).put()
					elif arg.startswith('foursquare'):
						Foursquare(
							contact = new_studio.key,
							foursquare = args[arg],
							primary = primary
							).put()
					elif arg.startswith('facebook'):
						Facebook(
							contact = new_studio.key,
							facebook = args[arg],
							primary = primary
							).put()
					elif arg.startswith('twitter'):
						Twitter(
							contact = new_studio.key,
							twitter = args[arg],
							primary = primary
							).put()
					elif arg.startswith('tumblr'):
						Tumblr(
							contact = new_studio.key,
							tumblr = args[arg],
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
		except ValidationError:
			# Error, so re-render form with error message
			error += '%s: %s' % (sys.exc_info()[0], sys.exc_info()[1])

			self.render('admin_studio_create.html', active_nav = 'studio', args = args, num_fields = self.num_fields(self.request.arguments()), error = error)

class AdminEdit(AdminStudio):
	def get(self, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get studio
		studio = ancestor_key.get()

		# Assemble args to pass to template
		db_args = {}
		args = {}

		# First get all props from db via Contact.props
		for k, v in studio.props().iteritems():
			try:
				db_args[k] = v.fetch()
			except AttributeError:
				if k != 'class': db_args[k] = getattr(studio,k)

		# Then translate db props into args dict for template
		for prop, value in db_args.iteritems():
			try: 
				# .sort() will except on non-list, as opposed to sorted()
				value.sort()

				# put primary item in front
				if len(value) > 1: value.sort(key = lambda x: x.primary, reverse = True)
			
				# go through list and map to form fields					
				if not args.get('ma_toggle') or args.get('ma_toggle') != 'yes': args['ma_toggle'] = 'no'

				# args are set to empty for multis so that an empty form field gets displayed
				if prop == 'email':
					args['email'] = True and [('%s-%s' % (value.index(item)+1,item.key.id()),item.email) for item in value] or [('','')]
				elif prop == 'phone':
					args['phone'] = True and [('%s-%s' % (value.index(item)+1,item.key.id()),{'phone_number':item.number,
															  'phone_type':item.phone_type,
															  'country_code':item.country_code}) for item in value] or [('',{'phone_number':'',
															  																 'phone_type':'',
															  																 'country_code':''})]
				elif prop == 'website':
					args['website'] = True and [('%s-%s' % (value.index(item)+1,item.key.id()),item.url) for item in value] or [('','')]
				elif prop == 'gallery':
					args['gallery'] = True and [('%s-%s' % (value.index(item)+1,item.key.id()),item.url) for item in value] or [('','')]
				elif prop == 'instagram':
					args['instagram'] = True and [('%s-%s' % (value.index(item)+1,item.key.id()),item.instagram) for item in value] or [('','')]
				elif prop == 'foursquare':
					args['foursquare'] = True and [('%s-%s' % (value.index(item)+1,item.key.id()),item.foursquare) for item in value] or [('','')]
				elif prop == 'facebook':
					args['facebook'] = True and [('%s-%s' % (value.index(item)+1,item.key.id()),item.facebook) for item in value] or [('','')]
				elif prop == 'twitter':
					args['twitter'] =  True and [('%s-%s' % (value.index(item)+1,item.key.id()),item.twitter) for item in value] or [('','')]
				elif prop == 'tumblr':
					args['tumblr'] =  True and [('%s-%s' % (value.index(item)+1,item.key.id()),item.tumblr) for item in value] or [('','')]
				elif prop == 'address' and value:
					args['street'] = value[0].street
					args['locality'] = value[0].locality
					args['subdivision'] = value[0].subdivision
					args['country'] = value[0].country
					args['postal_code'] = value[0].postal_code
				elif prop == 'mailing_address' and value:
					args['ma_toggle'] = 'yes'
					args['ma_street'] = value[0].street
					args['ma_locality'] = value[0].locality
					args['ma_subdivision'] = value[0].subdivision
					args['ma_country'] = value[0].country
					args['ma_postal_code'] = value[0].postal_code

			except AttributeError:
				# There was no list, so just put prop itself
				if prop != 'class':
					if hasattr(value,prop): args[prop] = getattr(value, prop)
					else: args[prop] = value

		args['skey'] = pagename

		self.render('admin_studio_edit.html', active_nav = 'studio', args = args, num_fields = self.num_fields(args))

	def post(self, pagename):
		# Collect all POSTed arguments
		args = {arg:self.request.get(arg) for arg in self.request.arguments()}

		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get studio
		studio = ancestor_key.get()

		try:
			raise_it, error = self.validate_args(args)

			# Convert args to Edit format
			args_edit = {}
			for arg in args:
				a = arg.split('-')[0]
				if (a in Contact.prop_names() or a == 'phone_number') and a not in ['phone_type','country_code']:
					eid = arg.split('-',1)[1]

					if a == 'phone_number' and not args_edit.get('phone'): args_edit['phone'] = []
					elif not args_edit.get(a): args_edit[a] = []
					
					if a == 'phone_number':
						args_edit['phone'].append(args[arg] and \
							(eid,{'phone_number':args[arg],
							'phone_type':args['phone_type-%s' % (eid,)],
							'country_code':args['country_code-%s' % (eid,)]}) or \
								(eid,{'phone_number':'',
									  'phone_type':'',
									  'country_code':''}))
					else: 
						args_edit[a].append(args[arg] and (eid,args[arg]) or (eid,''))
				elif '-' not in arg:
					args_edit[a] = args[arg]
			
			args = args_edit

			# if any of the fields failed validation
			if raise_it: raise ValidationError('error')


			#####################
			# Put new data to DB
			#####################

			studio = self.path_to_key(args['skey']).get()

			info('args',args)

			for arg in args:
				primary_id = ''
				try:
					# Multi fields
					for item in sorted(args[arg], key = lambda x: x[0]):
						if item[1] and not primary_id:
							primary_id = item[0]
							break

					# Iterate over each field in multifield
					for item in args[arg]:
						if item[0] == primary_id: primary = True
						else: primary = False

						if '-' in item[0]:
							item_id = item[0].split('-')[1]
							item_db = ndb.Key(arg.capitalize(),int(item_id)).get()
						else: 
							item_db = ''

						if not item_db and item[1]:		# New field
							if arg == 'email':								
								Email(
									contact = studio.key,
									email = item[1],
									primary = primary
									).put()
							elif arg == 'phone' and item[1]['phone_type'] and \
													item[1]['phone_number'] and \
													item[1]['country_code']:
								Phone(
									contact = studio.key,
									phone_type = item[1]['phone_type'],
									country_code = item[1]['country_code'],
									number = item[1]['phone_number'],
									primary = primary										
									).put()
							elif arg == 'website':
								Website(
									contact = studio.key,
									url = item[1],
									primary = primary
									).put()
							elif arg == 'gallery':
								Gallery(
									contact = studio.key,
									url = item[1],
									primary = primary
									).put()
							elif arg == 'instagram':
								Instagram(
									contact = studio.key,
									instagram = item[1],
									primary = primary
									).put()
							elif arg == 'foursquare':
								Foursquare(
									contact = studio.key,
									foursquare = item[1],
									primary = primary
									).put()
							elif arg == 'facebook':
								Facebook(
									contact = studio.key,
									facebook = item[1],
									primary = primary
									).put()
							elif arg == 'twitter':
								Twitter(
									contact = studio.key,
									twitter = item[1],
									primary = primary
									).put()
							elif arg == 'tumblr':
								Tumblr(
									contact = studio.key,
									tumblr = item[1],
									primary = primary
									).put()
						elif item_db:
							# Removed field
							if item[1] == '' or (arg == 'phone' and item[1]['phone_number'] == ''):
								item_db.key.delete()
							# Updated fieldd
							elif arg == 'email' and item_db.email != item[1]:
								item_db.email = item[1]
							elif arg in ['website','gallery'] and item_db.url != item[1]:
								item_db.url = item[1]
							elif arg in ['instagram','foursquare','facebook','twitter','tumblr'] and getattr(item_db,arg) != item[1]:
								setattr(item_db,arg,item[1])
							# Phone special case
							elif arg == 'phone' and (item[1]['phone_number'] != item_db.number or \
													 item[1]['phone_type'] != item_db.phone_type or \
													 item[1]['country_code'] != item_db.country_code):
								item_db.number = item[1]['phone_number']
								item_db.phone_type = item[1]['phone_type']
								item_db.country_code = item[1]['country_code']

							# Put it
							if item[1] and arg != 'phone' or arg == 'phone' and item[1]['phone_number']:
								item_db.primary = primary
								item_db.put()
				except IndexError:
					pass

			# Put new address
			put_it = False
			studio_address = studio.address.get()
			for arg in ['street','locality','subdivision','country','postal_code']:
				if args[arg] != getattr(studio_address,arg):
					setattr(studio_address,arg,args[arg])
					put_it = True
			if put_it: studio_address.put()

			# Put new mailing address
			put_it = False
			studio_mailing_address = studio.mailing_address.get()
			if args.get('ma_toggle') == 'no' and studio_mailing_address: studio_mailing_address.key.delete()
			else:			
				for arg in ['ma_street','ma_locality','ma_subdivision','ma_country','ma_postal_code']:
					if studio_mailing_address and args.get(arg) != getattr(studio_mailing_address,arg.split('ma_')[1]):
						setattr(studio_mailing_address,arg.split('ma_')[1],args[arg])
						put_it = True
					elif not studio_mailing_address and args.get(arg):
						studio_mailing_address = MailingAddress(
																contact = studio.key,
																street = args['ma_street'],
																locality = args['ma_locality'],
																subdivision = args['ma_subdivision'],
																country = args['ma_country'],
																postal_code = args['ma_postal_code']
																)
						put_it = True
				if put_it: studio_mailing_address.put()

			# Put new name
			if args['name'] != studio.name:
				studio.name = args['name']
				studio.put()

			# Update key if address has changed
			if self.path_to_key('%s/%s/%s/%s' % (args['country'],args['subdivision'],args['locality'],studio.key.id())) != studio.key:
				'''
				New key needed.
				Need to change key for:
				- Contact
				- All query props
				'''

				''' Getting all query props '''
				# Set new and old key
				new_key = self.path_to_key('%s/%s/%s/%s' % (args['country'],args['subdivision'],args['locality'],studio.key.id()))
				old_key = studio.key

				# Go through properties and reset all query properties
				for prop in studio.props():
					if hasattr(studio,prop):
						try:
							q_attrs = getattr(studio,prop).fetch()
							for attr in q_attrs:
								attr.contact = new_key
								attr.put()
						except AttributeError:
							pass

				# Create new studio
				studio.key = new_key
				studio.put()

				# Delete old studio
				old_key.delete()

				# Create Country, Subdivision, and/or Locality if they don't already exist
				country = args['country']
				subdivision = args['subdivision']
				locality = args['locality']

				Country(
					id = '%s' % (country,),
					display_name = COUNTRIES[country]['name']
					).put()
				Subdivision(
					parent = ndb.Key('Country', country),
					id = args['subdivision'],
					display_name = COUNTRIES[country]['subdivisions'][subdivision]
					).put()
				Locality(
					parent = ndb.Key('Country', country, 'Subdivision', subdivision),
					id = locality,
					display_name = locality
					).put()

			self.redirect('/admin/models/studio/view%s' % (self.key_to_path(studio.key)))
		except ValidationError:
			# Error, so re-render form with error message
			error += '%s: %s' % (sys.exc_info()[0], sys.exc_info()[1])

			self.render('admin_studio_edit.html', active_nav = 'studio', args = args, num_fields = self.num_fields(args), error = error)		

class AdminView(BaseHandler):
	def get(self, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get studio
		studio = ancestor_key.get()

		# Exchange country and subdivision id names for more readable names (e.g. "Pennsylvania" instead of "US-PA")
		studio.country = COUNTRIES[studio.address.get().country]['name']
		studio.subdivision = COUNTRIES[studio.address.get().country]['subdivisions'][studio.address.get().subdivision]

		try:
			if studio.mailing_address.get():
				studio.ma_country = COUNTRIES[studio.mailing_address.get().country]['name']
				studio.ma_subdivision = COUNTRIES[studio.mailing_address.get().country]['subdivisions'][studio.mailing_address.get().subdivision]
		except:
			pass

		# Tag on the edit and delete links
		studio.edit = '/admin/models/studio/edit/%s' % (pagename,)
		studio.delete = '/admin/models/studio/delete/%s' % (pagename,)

		# Call the template
		self.render('admin_studio_view.html', active='models', active_nav = 'studio', studio = studio)

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
			for prop_name,prop in ancestor_key.get().props().iteritems():
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