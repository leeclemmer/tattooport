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
		refresh_shop(shop_cache_id)

def refresh_shop(shop_cache_id):
	from main import *

	# Using a specific Instagram user to make IG API call needing access_token
	access_token = InstagramUser.by_id(keys.IG_APPUSER).access_token

	api = BaseHandler.get_instagram_api(access_token=access_token)

	# If shops with the same name, compare IDs
	# There is chance of same ID and same name... 
	# ... very remote (let's hope)
	shop_name, sid = shop_cache_id.split('/')
	shop_name = urllib.unquote_plus(shop_name)
	shop = ShopPage.get_shop(shop_name, sid)

	media, next = ShopPage.get_shop_response(api, shop, sid)

	info('caching shop', shop.name)

	return memcache.set(shop_cache_id, media, time=60*60*6)



