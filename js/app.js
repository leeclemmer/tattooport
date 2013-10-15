// Hide mobile address bar
window.addEventListener("load",function() {
	setTimeout(function(){
		window.scrollTo(0, 1);
	}, 0);
});

function forEach(array, action) {
	for (var i=0; i < array.length; i++) {
		action(array[i]);
	}
}

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

$(function() {
	photos = new Array();

	call_api();

	function call_api(api_url) {
		if (typeof $_API_URL === 'undefined') {
			api_url = '';
		} else {
			// Set defaul value for api_url; see http://bit.ly/RlOOZA
			api_url = typeof api_url !== 'undefined' ? api_url : $_API_URL;
		}

		if (api_url.substring(0, 4) == 'http' || endsWith(api_url, 'json'))  {
			// encode space as "+"s
			if (api_url.indexOf(' ') > -1) {
				api_url = api_url.replace(' ','+');
			}

			// Show head for foursquare streams
			if (api_url.indexOf('locations') > -1) {
				$('#location-photo-header').show();
			}

			// GetJSON from apiurl and call on_api_load
			$.getJSON(url=api_url,
				  callback=on_api_load);
		}
	}

	function on_api_load(data) {
		// HTML snippets for stream page
		var single_user_photo_div = '<div class="col-sm-6 col-md-4 col-lg-3 photo-col {{username}} {{igid}}"> \
	                    <div class="photo"> \
	                    	<a data-toggle="modal" href="#media-modal"> \
	                        <img data-original="{{img_src}}" src="/img/1x1_2a2a2a.gif" class="lazy" data-igid="{{igid}}" width="316" height="316"> \
	                        </a> \
	                        <div class="stream-photo-meta stream-photo-meta-bottom"> \
                    			<div class="likes-count {{liked_class}}"><i class="icon-heart"></i> <span class="likes-number">{{likes_count}}</span></div> \
                    			<!--<div class="comment-count"><i class="icon-comment"></i> {{comment_count}}</div>--> \
                    		</div> \
	                    </div> \
	                </div>';

		var multi_user_photo_div = '<div class="col-sm-6 col-md-4 col-lg-3 photo-col {{username}} {{igid}}"> \
	                    <div class="photo"> \
	                        <div class="stream-photo-meta stream-photo-meta-top"> \
                    			<div class="photo-author"> \
                    				<img class="img-responsive img-circle" src="{{profile_picture}}"> \
                    				<a href="/i/{{username}}">{{username}}</a> \
                    			</div> \
                    		</div> \
	                    	<a data-toggle="modal" href="#media-modal"> \
	                        <img data-original="{{img_src}}" src="/img/1x1_2a2a2a.gif" class="lazy" data-igid="{{igid}}" width="316" height="316"> \
	                        </a> \
	                        <div class="stream-photo-meta stream-photo-meta-bottom"> \
                    			<div class="likes-count {{liked_class}}"><i class="icon-heart"></i> <span class="likes-number">{{likes_count}}</span></div> \
                    			<!--<div class="comment-count"><i class="icon-comment"></i> {{comment_count}}</div>--> \
                    		</div> \
	                    </div> \
	                </div>';

	    var photo_div = '';

	    // Pick either single or multi user HTML snippet
	    if (data.meta.page_type == 'multi_user') { photo_div = multi_user_photo_div; }
	    else { photo_div = single_user_photo_div; }

	    // HTML snippet for profile images/links
	    var single_contact_div = '<div class="col-xs-4 col-sm-2 col-md-2 col-lg-2 single-contact-col {{username}}"> \
			    <a href="/i/{{username}}"> \
			      <img class="img-circle img-responsive" src="{{profile_picture}}"> \
			    <div class="author">{{username}}</div></a> \
			  </div>';
 
		if (data.meta.code == 200) {
			var re = ''

			// Insert HTML
			for (i=0; i<data.data.length; i++) {				
				// Photos
				photo = data.data[i];
				photos[photo.id] = photo;

				// Popular Shops & Artists
				if (i < 5 && data.meta.page_type == 'multi_user') {
					re = /{{profile_picture}}/g;
					single_contact_html = single_contact_div.replace(re,photo.user.profile_picture);

					re = /{{username}}/g;
					single_contact_html = single_contact_html.replace(re,photo.user.username);
					$('#pop-shops-artists .view-all').before(single_contact_html);
				}
				
				re = /{{img_src}}/g;
				html_to_append = photo_div.replace(re,photo.images.low_resolution.url);

				re = /{{igid}}/g;
				html_to_append = html_to_append.replace(re,photo.id);

				re = /{{liked_class}}/g;
				var liked_class = '';
				if (photo.user_has_liked && $_ACCESS_TOKEN) liked_class = 'liked';
				html_to_append = html_to_append.replace(re,liked_class);

				re = /{{likes_count}}/g;
				html_to_append = html_to_append.replace(re,photo.likes.count);

				re = /{{username}}/g;
				html_to_append = html_to_append.replace(re,photo.user.username);

				if (data.meta.source == 'tp_cache') {
					// Multi user stream page
					re = /{{profile_picture}}/g;
					html_to_append = html_to_append.replace(re,photo.user.profile_picture);

					re = /{{comment_count}}/g;
					html_to_append = html_to_append.replace(re,photo.comments.count);
				}

				$('.view-all').show();
				
				$('#media-holder').append(html_to_append);
				$('#media-holder img.lazy:last').lazyload({ effect: "fadeIn", threshold: 600 });
			}

			$('#media-holder').append('<img class="lazy" style="display:none">')

			// Bindings
			bind_photo_actions(data);
		} else {
			$('#media-holder').append("<div class='col-lg-12'><p>Sorry no pictures currently... try again later?</p></div>");
		}

		// Remove loading gif
		$('.ajax-loader').remove();
		$('.stream-page h1').show();
		$('.stream-page h2').show();
		$('.hide-while-loading').show();
		$('#loadmore').removeClass('button-loading');
	}

	function bind_photo_actions(data) {
		// *** Insert Load button binding
		insert_load_button();		
		function insert_load_button() {
			var load_more_button = '<button class="btn btn-lg btn-primary" id="loadmore">Load more</button>';

			// Insert load more button
			if (data.pagination.next_url) {
				if ($('#loadmore').length == 0) {
					$(load_more_button).insertAfter('#media-holder');
				};
				$('#loadmore').off().on('click', function() {
					$(this).addClass('button-loading');

					var next_url = data.pagination.next_url;
					if (next_url.indexOf('api.instagram') != -1) {
						next_url = next_url + '&callback=?'
					};

					call_api(api_url=next_url);
				});
			} else {
				$('#loadmore').remove()
			}
		}

		// *** Launch Modal Bindings
		if (document.width >= 768) {
			// only bind for tablet or larger
			$('.lazy').bind('click', function() {
				load_modal.call(this);
			});
		} else {
			$('.photo>a').removeAttr('href').on('click', function() { return null; });
		}

		function load_modal(igid) {
			igid = typeof igid !== 'undefined' ? igid : $(this).attr('data-igid');
			
			$('#media-modal .modal-body').children().remove();

			// Get previous and next image
			var data_prev = $(this).closest('.photo-col').prev().find('img.lazy');
			var data_next = $(this).closest('.photo-col').next().find('img.lazy');
			data_prev_id = data_prev.length > 0 ? data_prev.attr('data-igid') : null;
			data_next_id = data_next.length > 0 ? data_next.attr('data-igid') : null;

			$(document).off('keydown');
			
			// Previous image binding
			if (data_prev_id) {
				$('#media-modal .btn-prev i').show();
				$('#media-modal .btn-prev').off().on('click', function() {
					load_modal.call(data_prev, data_prev_id);
				});

				// Bind left key
				$(document).keydown(function(e) {
					var code = (e.keyCode ? e.keyCode : e.which);
					if(code == 37) { 
						load_modal.call(data_prev, data_prev_id);
						return false;
					}
				});
			} else {
				$('#media-modal .btn-prev i').hide();
			}

			// Next image binding
			if (data_next_id) {
				$('#media-modal .btn-next i').show();
				$('#media-modal .btn-next').off().on('click', function() {
					load_modal.call(data_next, igid=data_next_id);
				});

				// Bind right key
				$(document).keydown(function(e) {
					var code = (e.keyCode ? e.keyCode : e.which);
					if(code == 39) { 
						load_modal.call(data_next, igid=data_next_id);
						return false;
					}
				});
			} else {
				$('#media-modal .btn-next i').hide();
			}

			// Attach ID
			$('.modal-content').attr('id',igid);

			// Render photo
			modal_html = '<img src="' + photos[igid].images.standard_resolution.url + '" class="img-responsive media-modal">';
			$('#media-modal .modal-body').append(modal_html);

			// Render meta
			$('#media-modal .modal-meta').children().remove();
			modal_author = '<div class="photo-author"> \
								<img class="img-responsive img-circle" \
									 src="' + photos[igid].user.profile_picture + '"> ' + 
								'<a href="/i/' + photos[igid].user.username + '">' + 
								photos[igid].user.username + '</a>' + 
							'</div>';

			var likes_count = 0;
			if (photos[igid].likes.count) likes_count = parseInt($('.' + igid + ' .likes-count .likes-number').text());

			var liked_class = '';
			var media_id = $('.modal-content').attr('id');
			if ($('.' + media_id + ' .photo .stream-photo-meta .likes-count').hasClass('liked')) liked_class = ' liked';
			modal_like_count = '<div class="likes-count' + liked_class + '"><i class="icon-heart"></i> <span class="likes-number">' + likes_count + '</span></div>';
			
			var comments_count = 0;
			if (photos[igid].comments.count) comments_count =  photos[igid].comments.count;
			modal_comment_count = '<div class="comment-count"><i class="icon-comment"></i> ' + comments_count + '</div>';

			var caption = '';
			if (photos[igid].caption) caption = photos[igid].caption.text;
			modal_caption = '<div class="caption">' + caption + '</div>';

			$('#media-modal .modal-meta').append(modal_author).append(modal_like_count).append(modal_comment_count).append(modal_caption);

			// Bind
			bind_like_button();
		}

		// Bind Like button
		// bind_like_button();
		function bind_like_button() {
			if ($_ACCESS_TOKEN) {
				$('.likes-count').off().bind('click', function() {
					var in_modal = true;
					var media_id = $(this).parents('.modal-content').attr('id');

					if (media_id === undefined) { /// otherwise
						var in_modal = false;
						media_id = $(this).parents('.photo-col').find('a img:first').attr('data-igid');
					}

					// Call server proxy to like/unlike
					if ($(this).hasClass('liked')) {
						$.get('/igm/unlike/' + media_id);
					} else {
						$.get('/igm/like/' + media_id);
					}

					// Update UI
					if (in_modal) {
						// We're in a modal and changing the count of grid view
						bind_like_button_action.apply($('.' + media_id + ' .likes-count'));
					}

					bind_like_button_action.apply(this);				
				});

				function bind_like_button_action() {
					var likes = parseInt($(this).children('.likes-number').text());

					if ($(this).hasClass('liked')) {
						$(this).children('.likes-number').text(likes - 1);
					} else {
						$(this).children('.likes-number').text(likes + 1);
					}

					$(this).toggleClass('liked');
				}				
			}
		}
	}

	// Wrapper to return instagram api url
	function ig_api_url(endpoint) {
		var base_url = "https://api.instagram.com/v1";
		var at = "?access_token=" + $_ACCESS_TOKEN;
		var cb = "&callback=?";
		return base_url + endpoint + at + cb;
	}

	// Returns IG api url for user
	function ig_users_userid_url(user_id) {
		return ig_api_url('/users/' + user_id);
	}

	// Returns IG api url for media likes
	function ig_media_mediaid_likes_url(media_id) {
		return ig_api_url('/media/' + media_id + '/likes');
	}

	// Fetches JSON response for user id call
	function ig_users_userid(user_id, callback, params) {
		$.getJSON(url=ig_users_userid_url(user_id),
				  function (data) {
				  	callback(data, params);
				  });
	}

	// Inserts profile picture into element
	function insert_profile_picture(data, element) {
		if (data.meta.code == 200) {
			$(element).find('img:first').attr('src',data.data.profile_picture);
		}
	}
});
