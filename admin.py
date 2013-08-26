#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Admin Interface Handlers '''

# internal
from google.appengine.datastore.datastore_query import Cursor

from main import *

class ValidationError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class AdminMain(BaseHandler):
	def get(self):
		self.render('admin_main.html', 
					title='Main',
					active = 'admin')

class AdminModels(BaseHandler):
	def get(self):
		curs = Cursor(urlsafe = self.request.get('cursor'))
		studios, next_curs, more = Studio.query().order(-Studio.last_edited).fetch_page(10, start_cursor = curs)
		if studios:
			studios = [{'name':studio.name, 
						'last_edited':studio.last_edited, 
						'link':'/admin/models/studio/view%s' % \
								(self.key_to_path(studio.key))} 
							for studio in studios]
			self.render('admin_models.html', 
						title='Data Models', 
						active = 'models', 
						studios = studios, 
						next_curs = next_curs.urlsafe(), 
						more = more)
		else:
			self.render('admin_models.html', 
						title='Data Models', 
						active = 'models', 
						studios = [], 
						next_curs = '', 
						more = '')

class AdminStudio(BaseHandler):
	def get(self, pagename):
		try:
			self.render('admin_studio_%s.html' % (pagename), 
						active='models',
						active_nav = 'studio')
		except jinja2.TemplateNotFound:
			self.redirect('/admin/models')

	def valid_name(self, name):
		NAME_RE = re.compile(r"^[!:.,'\sa-zA-Z0-9_-]{3,250}$")
		return NAME_RE.match(name)

	def valid_email(self, email):
		EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
		return EMAIL_RE.match(email)

	def valid_phone_number(self, phone_number):
		PHONE_NUMBER_RE = re.compile(r"^[0-9-.\s()+]+$")
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
		return country in COUNTRIES

	def valid_subdivision(self, subdivision):
		subdivisions = [[sub for sub in COUNTRIES[country].get('subdivisions')] 
			for country in COUNTRIES if COUNTRIES[country]['subdivisions']]
		subdivisions = [item for sublist in subdivisions for item in sublist]
		return subdivision in subdivisions			

	def valid_postal_code(self, postal_code):
		POSTAL_CODE_RE = re.compile(r"^.[a-zA-Z0-9-\s]+$")
		return POSTAL_CODE_RE.match(postal_code)

	def valid_toggle(self, toggle):
		return toggle in ['yes','no']

	def validate_args(self, args, model_kind):
		''' Takes list of args and validates them against validation rules.
			Returns (True/False, error)'''
		error = ''
		raise_it = False

		# Name validation
		if model_kind == 'studio' and not args.get('name'):
			error += 'Studio must have a name'
			raise_it = True
		elif model_kind == 'artist' and not args.get('display_name'):
			error += 'Artist must have a display name'
			raise_it = True

		# Traverse arguments and run against validation function
		for k,v in {k:v for k,v in args.iteritems() if v}.iteritems():
			arg = k.split('-')[0]
			# Handle multi_field args
			if arg in Contact.prop_names() \
			or arg in ['phone_number','phone_type','country_code']:
				if not self.validation_funcs[arg](self, v):
					error += '%s field: "%s" is in a wrong format. Try again. # ' \
							 % (k.capitalize(), v)
					raise_it = True

				# Special case to make sure all 3 phone fields are filled out
				ext = ''
				if len(k.split('-')) > 1: ext = '-%s' % (k.split('-',1)[1],)
				if k.startswith('phone_number') \
					and (not args['country_code%s' % (ext,)] \
					or not args['phone_type%s' % (ext,)] \
					or not args['phone_number%s' % (ext,)]):
					error += 'Please fill in all three phone fields. #'
					raise_it = True
			# Single field args
			elif k != 'skey' and not self.validation_funcs[arg](self, args.get(k)):
				error += '%s field: "%s" is in a wrong format. Try again. # ' % (k, v)
				raise_it = True

		return (raise_it,error)

	def put_studio(self, country, subdivision, locality, name):
		parent = ndb.Key('Country', country,
					  'Subdivision', subdivision,
					  'Locality', locality)
		new_studio = Studio(parent=parent, name=name)
		new_studio.put()
		return new_studio

	def put_artist(self, display_name, first_name='', last_name=''):
		new_artist = Artist(display_name=display_name,
							first_name=first_name,
							last_name=last_name)
		new_artist.put()
		return new_artist

	def put_email(self, key, email, primary):
		Email(
			contact=key,
			email=email,
			primary=primary
			).put()

	def put_phone(self, key, phone_type,
				  country_code, number, primary):
		Phone(
			contact=key,
			phone_type=phone_type,
			country_code=country_code,
			number=number,
			primary=primary
			).put()

	def put_website(self, key, url, primary):
		Website(
			contact=key,
			url=url,
			primary=primary
			).put()

	def put_gallery(self, key, url, primary):
		Gallery(
			contact=key,
			url=url,
			primary=primary
			).put()

	def put_instagram(self, key, instagram, primary):
		Instagram(
			contact=key,
			instagram=instagram,
			primary=primary
			).put()

	def put_foursquare(self, key, foursquare, primary):
		Foursquare(
			contact=key,
			foursquare=foursquare,
			primary=primary
			).put()

	def put_facebook(self, key, facebook, primary):
		Facebook(
			contact=key,
			facebook=facebook,
			primary=primary
			).put()

	def put_twitter(self, key, twitter, primary):
		Twitter(
			contact=key,
			twitter=twitter,
			primary=primary
			).put()

	def put_tumblr(self, key, tumblr, primary):
		Tumblr(
			contact=key,
			tumblr=tumblr,
			primary=primary
			).put()

	def put_mailing_address(self, key, street, locality,
							subdivision, country, postal_code):
		MailingAddress(
			contact=key,
			street=street,
			locality=locality,
			subdivision=subdivision,
			country=country,
			postal_code=postal_code
			).put()

	def put_address(self, key, street, locality, subdivision,
					country, postal_code):
		addr = Address(
			contact=key,
			street=street,
			locality=locality,
			subdivision=subdivision,
			country=country,
			postal_code=postal_code,
			location=self.geo_pt('%s %s %s %s %s' %
							(street,
							locality,
							subdivision.split('-')[1],
							country,
							postal_code)))
		addr.update_location()
		addr.put()

		coun = Country(
			id=country,
			display_name=COUNTRIES[country]['name'],
			location=self.geo_pt('%s' % \
				(COUNTRIES[country]['name'],))
			)
		coun.update_location()
		coun.put()

		subd = Subdivision(
			parent=ndb.Key('Country', country),
			id=subdivision,
			display_name=COUNTRIES[country]['subdivisions'][subdivision],
			location=self.geo_pt('%s %s' % \
				(COUNTRIES[country]['subdivisions'][subdivision],
					COUNTRIES[country]['name'])))
		subd.update_location()
		subd.put()

		loca = Locality(
			parent=ndb.Key('Country', country,'Subdivision', subdivision),
			id=locality,
			display_name=locality,
			location=self.geo_pt('%s %s %s %s' %
							(locality,
							subdivision.split('-')[1],
							country,
							postal_code)))
		loca.update_location()
		loca.put()

	def put_relationship(self, studio, artist, relationship):
		StudioArtist(
			studio=studio,
			artist=artist,
			relationship=relationship).put()

	# Validation functions
	validation_funcs = {'name':valid_name,
						'display_name':valid_name,
						'first_name':valid_name,
						'last_name':valid_name,
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
	def get(self, model_kind):
		studio = self.request.get('studio')
		artist = self.request.get('artist')

		self.render('admin_create.html',
					active_nav=model_kind,
					args={},
					num_fields={},
					studio=studio,
					artist=artist)

	def post(self, model_kind):
		# Collect all POSTed arguments
		args = {arg:self.request.get(arg) for arg in self.request.arguments()}

		# Vars if created to create relationship
		if 'studio' in args: studio = args.pop('studio')
		if 'artist' in args: artist = args.pop('artist')
		if 'relationship' in args: relationship = args.pop('relationship')
			
		try:
			raise_it, error = self.validate_args(args, model_kind)

			# if any of the fields failed validation
			if raise_it: raise ValidationError(error)

			# Put form fields into database
			if model_kind == 'studio':
				new_model = self.put_studio(
					country=args['country'],
					subdivision=args['subdivision'],
					locality=args['locality'],
					name=args['name'])

				self.put_relationship(
					studio=new_model.key,
					artist=self.path_to_key(artist),
					relationship=relationship)
			elif model_kind == 'artist':
				new_model = self.put_artist(
					display_name=args['display_name'],
					first_name=args.get('first_name'),
					last_name=args.get('last_name'))

				self.put_relationship(
					studio=self.path_to_key(studio),
					artist=new_model.key,
					relationship=relationship)

			# Traverse non-empty arguments
			for k,v in {k:v for k,v in args.iteritems() if v}.iteritems():
				primary = False
				ext = ''
				if len(k.split('-')) <= 1: primary = True
				else: ext = '-%s' % (k.split('-')[1])

				if k.startswith('email'):
					self.put_email(
						key=new_model.key,
						email=v,
						primary=primary)
				elif k.startswith('phone_number'):
					self.put_phone(
						key=new_model.key,
						phone_type=args['phone_type%s' % (ext,)],
						country_code=args['country_code%s' % (ext,)],
						number=v,
						primary=primary)
				elif k.startswith('website'):
					self.put_website(
						key=new_model.key,
						url=v,
						primary=primary)
				elif k.startswith('gallery'):
					self.put_gallery(
						key=new_model.key,
						url=v,
						primary=primary)
				elif k.startswith('instagram'):
					self.put_instagram(
						key=new_model.key,
						instagram=v,
						primary=primary)
				elif k.startswith('foursquare'):
					self.put_foursquare(
						key=new_model.key,
						foursquare=v,
						primary=primary)
				elif k.startswith('facebook'):
					self.put_facebook(
						key=new_model.key,
						facebook=v,
						primary=primary)
				elif k.startswith('twitter'):
					self.put_twitter(
						key=new_model.key,
						twitter=v,
						primary=primary)
				elif k.startswith('tumblr'):
					self.put_tumblr(
						key=new_model.key,
						tumblr=v,
						primary=primary)
				elif k == 'country':
					self.put_address(
						key=new_model.key,
						street=args['street'],
						locality=args['locality'],
						subdivision=args['subdivision'],
						country=v,
						postal_code=args['postal_code'])
				elif k == 'ma_country':
					self.put_mailing_address(
						key=new_model.key,
						street=args['ma_street'],
						locality=args['ma_locality'],
						subdivision=args['ma_subdivision'],
						country=v,
						postal_code=args['ma_postal_code'])

			self.redirect('/admin/models/%s/view%s' % (model_kind, self.key_to_path(new_model.key)))
		except ValidationError:
			# Error, so re-render form with error message
			error += '%s: %s' % (sys.exc_info()[0], sys.exc_info()[1])

			self.render('admin_create.html',
						active_nav=model_kind,
						args=args,
						num_fields=self.num_fields(self.request.arguments()),
						error=rror)

class AdminEdit(AdminStudio):
	def get(self, model_kind, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get model
		model = ancestor_key.get()

		# Assemble args to pass to template
		db_args = {}
		args = {}

		# First get all props from db via Contact.props
		for k, v in model.props().iteritems():
			try:
				db_args[k] = v.fetch()
			except AttributeError:
				if k != 'class': db_args[k] = getattr(model,k)

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
					args['phone'] = True and \
						[('%s-%s' % (value.index(item)+1, \
						 	item.key.id()),
							{'phone_number':item.number,
							 'phone_type':item.phone_type,
						 	 'country_code':item.country_code}) \
						 	for item in value] or [('',{'phone_number':'',
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

		self.render('admin_edit.html',
					active_nav=model_kind,
					args=args,
					num_fields=self.num_fields(args))

	def post(self, model_kind, pagename):
		# Collect all POSTed arguments
		args = {arg:self.request.get(arg) for arg in self.request.arguments()}

		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get model
		model = ancestor_key.get()

		try:
			raise_it, error = self.validate_args(args, model_kind)

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

			model = self.path_to_key(args['skey']).get()

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
								self.put_email(
									model.key,
									item[1],
									primary)
							elif arg == 'phone' \
								and item[1]['phone_type'] \
								and item[1]['phone_number'] \
								and item[1]['country_code']:
								self.put_phone(
									key=model.key,
									phone_type=item[1]['phone_type'],
									country_code = item[1]['country_code'],
									number = item[1]['phone_number'],
									primary = primary)
							elif arg == 'website':
								self.put_website(
									key=model.key,
									url=item[1],
									primary=primary)
							elif arg == 'gallery':
								self.put_gallery(
									key=model.key,
									url=item[1],
									primary=primary)
							elif arg == 'instagram':
								self.put_instagram(
									key=model.key,
									instagram=item[1],
									primary=primary)
							elif arg == 'foursquare':
								self.put_foursquare(
									key=model.key,
									foursquare=item[1],
									primary=primary)
							elif arg == 'facebook':
								self.put_facebook(
									key=model.key,
									facebook=item[1],
									primary=primary)
							elif arg == 'twitter':
								self.put_twitter(
									key=model.key,
									twitter=item[1],
									primary=primary)
							elif arg == 'tumblr':
								self.put_tumblr(
									key=model.key,
									tumblr=item[1],
									primary=primary)
						elif item_db:
							# Removed field
							if item[1] == '' or (arg == 'phone' and item[1]['phone_number'] == ''):
								item_db.key.delete()
							# Updated fieldd
							elif arg == 'email' and item_db.email != item[1]:
								item_db.email = item[1]
							elif arg in ['website','gallery'] and item_db.url != item[1]:
								item_db.url = item[1]
							elif arg in ['instagram','foursquare','facebook',
										 'twitter','tumblr'] \
									 and getattr(item_db,arg) != item[1]:
								setattr(item_db,arg,item[1])
							# Phone special case
							elif arg == 'phone' and \
								(item[1]['phone_number'] != item_db.number or\
								item[1]['phone_type'] != item_db.phone_type or\
								item[1]['country_code'] != \
														item_db.country_code):
								item_db.number = item[1]['phone_number']
								item_db.phone_type = item[1]['phone_type']
								item_db.country_code = item[1]['country_code']

							# Put it
							if item[1] and arg != 'phone' \
										or arg == 'phone' \
										and item[1]['phone_number']:
								item_db.primary = primary
								item_db.put()
				except IndexError:
					pass

			if model_kind == 'studio':
				# Put new address
				put_it = False
				sa = model.address.get()
				for arg in ['street',
							'locality',
							'subdivision',
							'country',
							'postal_code']:
					if args[arg] != getattr(sa,arg):
						setattr(sa,arg,args[arg])
						put_it = True
				if put_it:
					sa.location = self.geo_pt('%s %s %s %s %s' %
													(sa.street,
													sa.locality,
													sa.subdivision.split('-')[1],
													sa.country,
													sa.postal_code))
					sa.update_location()
					sa.put()

				# Put new mailing address
				put_it = False
				sma = model.mailing_address.get()

				if args.get('ma_toggle') == 'no' and sma: sma.key.delete()
				else:			
					for arg in ['ma_street','ma_locality','ma_subdivision',
								'ma_country','ma_postal_code']:
						if sma and \
							args.get(arg) != \
							getattr(sma,arg.split('ma_')[1]):
							setattr(sma,
									arg.split('ma_')[1],
									args[arg])
							put_it = True
						elif not sma and args.get(arg):
							sma = MailingAddress(
								contact = model.key,
								street = args['ma_street'],
								locality = args['ma_locality'],
								subdivision = args['ma_subdivision'],
								country = args['ma_country'],
								postal_code = args['ma_postal_code'])
							put_it = True
					if put_it:
						sma.put()

				# Put new name
				if args['name'] != model.name:
					model.name = args['name']
					model.put()

				# Update key if address has changed
				path = '%s/%s/%s/%s' % (args['country'],
										args['subdivision'],
										args['locality'],
										model.key.id())
			elif model_kind == 'artist':
				if args['display_name'] != model.display_name:
					model.display_name = args['display_name']
				if args.get('first_name'):
					model.first_name = args['first_name']
				if args.get('last_name'):
					model.last_name = args['last_name']
				model.put()
				
				path = '%s' % (model.key.id(),)

			if self.path_to_key(path) != model.key:
				# Set new and old key
				new_key = self.path_to_key('%s/%s/%s/%s' % (args['country'],args['subdivision'],args['locality'],model.key.id()))
				old_key = model.key

				# Go through properties and reset all query properties
				for prop in model.props():
					if hasattr(model,prop):
						try:
							q_attrs = getattr(model,prop).fetch()
							for attr in q_attrs:
								attr.contact = new_key
								attr.put()
						except AttributeError:
							pass

				# Create new model
				model.key = new_key
				model.put()

				# Delete old model
				old_key.delete()

				# Create Country, Subdivision, and/or Locality if they don't already exist
				country = args['country']
				subdivision = args['subdivision']
				locality = args['locality']
				postal_code = args['postal_code']

				coun = Country(
					id=country,
					display_name=COUNTRIES[country]['name'],
					location=self.geo_pt('%s' % \
						(COUNTRIES[country]['name'],))
					)
				coun.put()
				coun.update_location()

				subd = Subdivision(
					parent=ndb.Key('Country', country),
					id=subdivision,
					display_name=COUNTRIES[country]['subdivisions'][subdivision],
					location=self.geo_pt('%s %s' % \
						(COUNTRIES[country]['subdivisions'][subdivision],
							COUNTRIES[country]['name'])))
				subd.put()
				subd.update_location()

				loca = Locality(
					parent=ndb.Key('Country', country,'Subdivision', subdivision),
					id=locality,
					display_name=locality,
					location=self.geo_pt('%s %s %s %s' %
									(locality,
									subdivision.split('-')[1],
									country,
									postal_code)))
				loca.put()
				loca.update_location()

			self.redirect('/admin/models/%s/view/%s' % (model_kind, path))
		except ValidationError:
			# Error, so re-render form with error message
			error += '%s: %s' % (sys.exc_info()[0], sys.exc_info()[1])

			self.render('admin_edit.html',
						active_nav=model_kind,
						args=args,
						num_fields=self.num_fields(args),
						error=error)		

class AdminView(BaseHandler):
	def get(self, model_kind, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		info('pagename',pagename)
		info('ancestor_key',ancestor_key)
		
		# Get studio
		model = ancestor_key.get()

		info('mode',model)

		# Tag on the edit and delete links
		model.edit = '/admin/models/%s/edit/%s' % (model_kind,pagename)
		model.delete = '/admin/models/%s/delete/%s' % (model_kind,pagename)

		# Call the template
		if model_kind == 'studio':
			# Exchange country and subdivision id names for more readable names (e.g. "Pennsylvania" instead of "US-PA")
			model.country = COUNTRIES[model.address.get().country]['name']
			model.subdivision = COUNTRIES[model.address.get().country]['subdivisions'][model.address.get().subdivision]

			try:
				if model.mailing_address.get():
					model.ma_country = COUNTRIES[model.mailing_address.get().country]['name']
					model.ma_subdivision = COUNTRIES[model.mailing_address.get().country]['subdivisions'][studio.mailing_address.get().subdivision]
			except:
				pass

			artists = [{'name':artist.artist.get().display_name,
					'rel':artist.relationship,
					'link':'/admin/models/artist/view/%s' % artist.artist.id(),
					'relid':artist.key.id()} \
					for artist in model.artists]

			self.render('admin_studio_view.html', 
						active='models', 
						active_nav=model_kind, 
						studio=model,
						artists=artists,
						breadcrumbs=self.path_to_breadcrumbs(pagename),
						map_url=self.static_map_url(model.address.get().location))
		elif model_kind == 'artist':
			studios = [{'name':studio.studio.get().name,
					'rel':studio.relationship,
					'link':'/admin/models/studio/view%s' % \
						self.key_to_path(studio.studio),
					'relid':studio.key.id()} \
					for studio in model.studios]

			self.render('admin_artist_view.html',
						active='models',
						active_nav=model_kind,
						artist=model,
						studios=studios)

	def post(self, model_kind, pagename):
		delrel = self.request.get('del-rel')
		ndb.Key(StudioArtist, int(delrel)).delete()
		self.redirect('/admin/models/%s/view/%s' % (model_kind, pagename))

class AdminDelete(BaseHandler):
	def get(self, model_kind, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get model
		model = ancestor_key.get()
		model.view = '/admin/models/model/view/%s' % (pagename,)

		# Call the template
		self.render('admin_delete.html',
					active='models',
					active_nav=model_kind,
					model=model)

	def post(self, model_kind, pagename):
		# Create ancestor key from URL path
		ancestor_key = self.path_to_key(pagename)
		
		# Get studio
		if model_kind == 'studio':
			name = ancestor_key.get().name
		elif model_kind == 'artist':
			name = ancestor_key.get().display_name

		# Call the template
		if self.request.get('delete') and self.request.get('delete') == 'yes':
			for prop_name,prop in ancestor_key.get().props().iteritems():
				try:
					info('deleting %s' % (prop_name,), prop)
					ndb.delete_multi([p.key for p in prop.fetch()])
				except AttributeError:
					pass
			# Delete studio
			ancestor_key.delete()
			self.render('admin_delete.html',
						active='models',
						active_nav=model_kind,
						name=name,
						confirmation=True)
		else:
			self.redirect('/admin/models/studio/delete/%s' % (pagename,))

class AdminStudioBrowse(BaseHandler):
	def get(self):
		''' Displays tree structure of country, subdivision, locality. '''
		regions = [[country,
					[[subdivision,
						[[locality,urllib.quote_plus(locality.key.id())] for locality in Locality.query_location(subdivision.key).order(Locality.display_name).fetch()]]
					for subdivision in Subdivision.query_location(country.key).order(Subdivision.display_name).fetch()]]
				for country in Country.query().order(Country.display_name).fetch()]

		self.render('admin_studio_browse.html',
					active='models',
					active_nav='studio',
					regions=regions)

class AdminStudioBrowseRegion(BaseHandler):
	def get(self, pagename):
		ancestor_key = self.path_to_key(pagename)
		regions = ''

		if ancestor_key.kind() == 'Locality':
			# If browsing city, search is a proximity search
			region_pt = ancestor_key.get().location
			results = Address.proximity_fetch(
				Address.query(),
				region_pt,
				max_results=10,
				max_distance=80467)
			results = sorted([addr.contact.get() for addr in results], key=lambda x: x.name)
		else:
			if ancestor_key.kind() == 'Country':
				regions = Subdivision.query_location(ancestor_key).fetch()
			elif ancestor_key.kind() == 'Subdivision':
				regions = Locality.query_location(ancestor_key).fetch()
			# Otherwise, results are direct members
			results = Studio.query_location(ancestor_key).order(Studio.name)
		results = zip(results,[self.key_to_path(result.key) for result in results])
		info('regions',regions)
		self.render('admin_studio_browse_region.html',
					active='models',
					active_nav='studio',
					results=results,
					regions=regions,
					breadcrumbs=self.path_to_breadcrumbs(pagename))

class AdminArtistBrowse(BaseHandler):
	def get(self):
		curs = Cursor(urlsafe=self.request.get('cursor'))
		artists, next_curs, more = Artist.query().order(-Artist.last_edited).fetch_page(10, start_cursor=curs)
		if artists:
			artists = [{'name':artist.display_name, 
						'last_edited':artist.last_edited, 
						'link':'/admin/models/artist/view%s' % \
								(self.key_to_path(artist.key))} 
							for artist in artists]
			self.render('admin_models.html', 
						title='Recent Artists', 
						active='models', 
						studios=artists, 
						next_curs=next_curs.urlsafe(), 
						more=more)
		else:
			self.render('admin_models.html', 
						title='No Recent Artists', 
						active='models', 
						studios=[], 
						next_curs='', 
						more='')

class AdminSearch(BaseHandler):
	def get(self, model_kind):
		q = self.request.get('q')
		studio = self.request.get('studio')
		artist = self.request.get('artist')
		results = ''

		if q:
			if model_kind == 'studio':
				# Searches beginning of name; see http://bit.ly/gCpc54 for more
				results = Studio.gql("WHERE name >= :1 AND name < :2",
					q, q + u"\ufffd").fetch()
				results = [{'name':result.name, 
						'last_edited':result.last_edited, 
						'link':'/admin/models/studio/view%s' % \
								(self.key_to_path(result.key))} 
							for result in results]
			elif model_kind == 'artist':
				results = Artist.gql("WHERE display_name >= :1 AND display_name < :2",
					q, q + u"\ufffd").fetch()
				results = [{'name':result.display_name, 
						'last_edited':result.last_edited, 
						'link':'/admin/models/artist/view%s' % \
								(self.key_to_path(result.key))} 
							for result in results]
			info('results',results)
		self.render('admin_search.html',
					title='Search %ss' % (model_kind.capitalize(),),
					active='models',
					active_nav=model_kind,
					results=results,
					q=q,
					studio=studio,
					artist=artist)

	def post(self, model_kind):
		studio = self.request.get('studio')
		artist = self.request.get('artist')
		relationship = self.request.get('relationship')

		if '/admin/models/studio/view/' in studio:
			studio = studio.split('/admin/models/studio/view/')[1]
		studio = self.path_to_key(studio)

		if '/admin/models/artist/view/' in artist:
			artist = artist.split('/admin/models/artist/view/')[1]
		artist = self.path_to_key(artist)

		if studio and artist and relationship:
			StudioArtist(
				studio=studio,
				artist=artist,
				relationship=relationship).put()
			self.redirect('/admin/models/studio/view%s' % \
				(self.key_to_path(studio)))
		else:
			logging.error('''Couldn't create relationship, something is missing.\nStudio = %s\nArtist=%s\nRelationship=%s''' % (studio,
																 artist, 
																 relationship))
		self.write((studio, artist, relationship))

app = webapp2.WSGIApplication(
	[('/admin/?', AdminMain),
	 ('/admin/models/?', AdminModels),
	 ('/admin/models/(studio|artist)/create/?', AdminCreate),
	 ('/admin/models/(studio|artist)/view/([\+\s,.\'()0-9a-zA-Z\/_-]*?)', AdminView),
	 ('/admin/models/(studio|artist)/edit/([\+\s,.\'()0-9a-zA-Z\/_-]*?)', AdminEdit),
	 ('/admin/models/(studio|artist)/delete/([\+\s,.\'()0-9a-zA-Z\/_-]*?)', AdminDelete),
	 ('/admin/models/studio/browse/?', AdminStudioBrowse),
	 ('/admin/models/studio/browse/([\+\s,.\'()0-9a-zA-Z\/_-]*?)', AdminStudioBrowseRegion),
	 ('/admin/models/(studio|artist)/search/?', AdminSearch),
	 ('/admin/models/studio/([0-9a-zA-Z]*?)', AdminStudio),
	 ('/admin/models/artist/browse/?', AdminArtistBrowse)], debug=True)