""" Contains all methods call by deferred.defer and their dependencies.
"""


def refresh_cache():
	from main import *

	# 1. Get list of all pages that need to be cached
	# 2. Check current cache to see if they're current
	# 3. Update missing or soon-to-expire cache

	# 1. Pages that need to be cached:
	# - Shop pages
	# - Artist pages
	# - Tag Pages
	
	# Shop pages
	regions = BaseHandler.regions_in_db()
	shops = []

	for country in regions:
		for subdivision in country[1]:
			for locality in subdivision[1]:
				shops.append(Studio.query_location(locality[0].key).fetch())

	shops = utils.flatten_list(shops)
	shops = ['%s/%s' % (urllib.quote_plus(shop.name),shop.key.id()) for shop in shops]
	for shop_cache_id in shops:
		shop_cache = memcache.get(shop_cache_id)
		if not shop_cache:
			refresh_shop(shop_cache_id)

def refresh_shop(shop_cache_id):
	from main import *

	# Using a specific Instagram user to make IG API call needing access_token
	access_token = InstagramUser.by_id(keys.IG_APPUSER).access_token

	api = BaseHandler.get_instagram_api(access_token=access_token)

	# If shops with the same name, compare IDs
	# There is chance of same ID and same name... 
	# ... very remote (let's hope)
	shop, sid = shop_cache_id.split('/')
	shop = urllib.unquote_plus(shop)
	for s in Studio.by_name(shop):
		if int(sid) == s.key.id():
			shop = s
			break

	media = 'Not available'
	next = None
	if shop.instagram.get() is not None:
		for ig in shop.instagram.fetch():
			if ig.primary == True and ig.user_id:
				media, next = api.user_recent_media(
					user_id=ig.user_id,
					count=12)
				break
	elif shop.foursquare.get() is not None:
		for fsq in shop.foursquare.fetch():
			if fsq.primary == True and fsq.location_id:
				location_id = fsq.location_id
				media, next = api.location_recent_media(
					count=12, 
					location_id=fsq.location_id)
				break

	return memcache.set(shop_cache_id, media, time=60*60*6)



