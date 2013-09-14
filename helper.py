''' Helper functions. '''
import socket 

from models import *
import utils
import keys

from instagram.client import InstagramAPI

def nearby_shops(locality_key, latlng=''):
	''' Proximity search for shops given a locality key. 
		Can also pass in a latlng direction. '''
	geocoords = latlng and latlng or locality_key.get().location
	try:
		results = Address.proximity_fetch(
			Address.query(),
			geocoords,
			max_results=10,
			max_distance=80467) # 50 miles
	except AttributeError:
		utils.catch_exception()
		results = ''
	return sorted([addr.contact.get() for addr in results], key=lambda x: x.name)

def shops_artists(shops):
	''' Given a list of shops, return all related artists. '''
	results = [[rel.artist.get() for rel in shop.artists.fetch()] for shop in shops]
	return utils.flatten_list(results)

def get_instagram_api(access_token=''):
	''' Helper function for quick access to instagram api. 
		Access token optional. If not given, API access is limited.
	'''
	return InstagramAPI(client_id=keys.IG_CLIENTID,
						client_secret=keys.IG_CLIENTSECRET,
						access_token=access_token)

def get_app_api():
	# Using a specific Instagram user to make IG API call needing access_token
	access_token = InstagramUser.by_id(keys.IG_APPUSER).access_token
	return get_instagram_api(access_token=access_token)

def get_contact(contact_type, contact_name, cid):		
	# If contact with the same name, compare IDs
	# There is chance of same ID and same name... 
	# ... very remote (let's hope)
	if contact_type == 'shop':
		contact_results = Studio.by_name(contact_name)
	elif contact_type == 'artist':
		contact_results = Artist.by_name(contact_name)
	else: return None

	for c in contact_results:
		if int(cid) == c.key.id():
			return c
			break

def get_contact_response(api, contact, cid, contact_type, max_id=''):
	media = None
	next = None

	if contact.instagram.get() is not None:
		for ig in contact.instagram.fetch():
			if ig.primary == True and ig.user_id:
				media, next = api.user_recent_media(
					user_id=ig.user_id,
					count=30, 
					max_id=max_id)
				break
	elif contact_type != 'artist' and contact.foursquare.get() is not None:
		for fsq in contact.foursquare.fetch():
			if fsq.primary == True and fsq.location_id:
				location_id = fsq.location_id
				media, next = api.location_recent_media(
					count=30, 
					location_id=fsq.location_id,
					max_id=max_id)
				break

	return (media, next)

def get_category_response(api, category, max_id=''):
	return api.tag_recent_media(
		count=30,
		tag_name=category,
		max_id=max_id)

def media_list_to_json(media_list, pagename='', page=-1):
	''' Takes a media list and converts it to JSON. '''
	media_list_dicts = []

	for media_item in media_list:
		mi_dict = adjust_media_item(utils.to_dict(media_item))
		media_list_dicts.append(mi_dict)

	return media_list_dicts

def ig_envelope(media_list, api_url='', page=-1, max_id='', 
				page_type='single_user'):
	''' Wraps a list of media items in IG API envelope. '''
	next_url = page != -1 and "%s?page=%d" % (api_url, page + 1) or None
	return {
		"pagination": {
			"next_url": next_url,
			"next_max_id": max_id
			},
		"meta": {
			"code": 200,
			"source": "tp_cache",
			"page_type": page_type
			},
		"data": media_list
		}

def adjust_media_item(mi_dict):
	''' Adjusts JSON version of media item to match IG API.
		Frankly instead of doing this I should just adapt
		Instagram library to give me straight IG response.
	'''
	# Things to come back to:
	# - attribution: null
	# - type: image - does python instagram cover videos?
	# - users_in_photo (not in API)

	if mi_dict.get('tags'):
		mi_dict['tags'] = [i['name'] for i in mi_dict['tags']]

	if mi_dict.get('location'):
		if mi_dict['location']['point'] is not None:
			mi_dict['location'] = dict(mi_dict['location'].items() +
							       mi_dict['location']['point'].items())
			del mi_dict['location']['point']

	if mi_dict.get('comments'):
		comments = {}

		comments['count'] = mi_dict['comment_count']
		del mi_dict['comment_count']

		comments['data'] = mi_dict['comments']

		for comment in comments['data']:
			comment['created_time'] = str(comment['created_at'])
			del comment['created_at']

			comment['from'] = comment['user']
			del comment['user']

		mi_dict['comments'] = comments

	mi_dict['created_time'] = str(mi_dict['created_time'])

	if mi_dict.get('likes'):
		likes = {}

		likes['count'] = mi_dict['like_count']
		del mi_dict['like_count']

		likes['data'] = mi_dict['likes']
		mi_dict['likes'] = likes

	if mi_dict.get('caption'):
		mi_dict['caption']['created_time'] = \
			str(mi_dict['caption']['created_at'])
		del mi_dict['caption']['created_at']

		mi_dict['caption']['from'] = mi_dict['caption']['user']
		del mi_dict['caption']['user']
	
	return mi_dict


