// Hide mobile address bar
window.addEventListener("load",function() {
	setTimeout(function(){
		window.scrollTo(0, 1);
	}, 0);
});

$(function() {
	call_api();

	photos = new Array();

	function call_api(api_url) {
		// Set defaul value for api_url; see http://bit.ly/RlOOZA
		api_url = typeof api_url !== 'undefined' ? api_url : $_API_URL;

		if (api_url.substring(0, 4) == 'http' || endsWith(api_url, 'json'))  {
			if (api_url.indexOf(' ') > -1) {
				// encode space as "+"
				api_url = api_url.replace(' ','+');
			}

			$.getJSON(url=api_url,
				  callback=on_api_load);
		}
	}

	function on_api_load(data) {
		var single_user_photo_div = '<div class="col-sm-6 col-md-4 col-lg-3 photo-col"> \
	                    <div class="photo"> \
	                    	<a data-toggle="modal" href="#media-modal"> \
	                        <img data-original="{{img_src}}" src="/img/1x1_2a2a2a.gif" class="lazy" data-igid="{{igid}}" width="316" height="316"> \
	                        </a> \
	                        <div class="stream-photo-meta stream-photo-meta-bottom"> \
                    			<div class="likes-count"><i class="icon-heart"></i> {{likes_count}}</div> \
                    			<!--<div class="comment-count"><i class="icon-comment"></i> {{comment_count}}</div>--> \
                    		</div> \
	                    </div> \
	                </div>';

		var multi_user_photo_div = '<div class="col-sm-6 col-md-4 col-lg-3 photo-col"> \
	                    <div class="photo"> \
	                        <div class="stream-photo-meta stream-photo-meta-top"> \
                    			<div class="photo-author"> \
                    				<img class="img-responsive img-circle" src="{{profile_picture}}">{{username}} \
                    			</div> \
                    		</div> \
	                    	<a data-toggle="modal" href="#media-modal"> \
	                        <img data-original="{{img_src}}" src="/img/1x1_2a2a2a.gif" class="lazy" data-igid="{{igid}}" width="316" height="316"> \
	                        </a> \
	                        <div class="stream-photo-meta stream-photo-meta-bottom"> \
                    			<div class="likes-count"><i class="icon-heart"></i> {{likes_count}}</div> \
                    			<!--<div class="comment-count"><i class="icon-comment"></i> {{comment_count}}</div>--> \
                    		</div> \
	                    </div> \
	                </div>';

	    var photo_div = '';

	    if (data.meta.page_type == 'multi_user') { photo_div = multi_user_photo_div; }
	    else { photo_div = single_user_photo_div; }

 
		if (data.meta.code == 200) {
			console.log(data.meta.source);
			// Insert photos
			for (i=0; i<data.data.length; i++) {
				photo = data.data[i];
				photos[photo.id] = photo;
				
				html_to_append = photo_div.replace('{{img_src}}',photo.images.low_resolution.url);
				html_to_append = html_to_append.replace('{{igid}}',photo.id);
				html_to_append = html_to_append.replace('{{likes_count}}',photo.likes.count);

				if (data.meta.source == 'tp_cache') {
					// Multi user stream page
					html_to_append = html_to_append.replace('{{profile_picture}}',photo.user.profile_picture);
					html_to_append = html_to_append.replace('{{username}}',photo.user.username);
					html_to_append = html_to_append.replace('{{comment_count}}',photo.comments.count);
				}
				
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
		$('#ajax-loader').remove();
		$('#loadmore').removeClass('button-loading');
	}

	function bind_photo_actions(data) {
		insert_load_button();

		// *** Insert Load button binding
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
			$('.photo a').removeAttr('href').on('click', function() { return null; });
		}

		function load_modal(igid) {
			igid = typeof igid !== 'undefined' ? igid : $(this).attr('data-igid');
			
			$('#media-modal .modal-body').children().remove();

			// Get previous and next image
			var data_prev = $(this).closest('.photo-col').prev().find('img.lazy');
			var data_next = $(this).closest('.photo-col').next().find('img.lazy');
			data_prev_id = data_prev.length > 0 ? data_prev.attr('data-igid') : null;
			data_next_id = data_next.length > 0 ? data_next.attr('data-igid') : null;
			
			// Previous image binding
			if (data_prev_id) {
				$('#media-modal .btn-prev i').show();
				$('#media-modal .btn-prev').off().on('click', function() {
					load_modal.call(data_prev, data_prev_id);
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
			} else {
				$('#media-modal .btn-next i').hide();
			}			

			// Render photo
			modal_html = '<img src="' + photos[igid].images.standard_resolution.url + '" class="img-responsive media-modal">';
			$('#media-modal .modal-body').append(modal_html);

			// Render meta
			$('#media-modal .modal-meta').children().remove();
			modal_author = '<div class="photo-author"> \
								<img class="img-responsive img-circle" \
									 src="' + photos[igid].user.profile_picture + '"> ' + 
								photos[igid].user.username + ' \
							</div>';

			var likes_count = 0;
			if (photos[igid].likes.count) likes_count = photos[igid].likes.count;
			modal_like_count = '<div class="likes-count"><i class="icon-heart"></i> ' + likes_count + '</div>';

			var comments_count = 0;
			if (photos[igid].comments.count) comments_count =  photos[igid].comments.count;
			modal_comment_count = '<div class="comment-count"><i class="icon-comment"></i> ' + comments_count + '</div>';

			var caption = '';
			if (photos[igid].caption) caption = photos[igid].caption.text;
			modal_caption = '<div class="caption">' + caption + '</div>';

			$('#media-modal .modal-meta').append(modal_author).append(modal_like_count).append(modal_comment_count).append(modal_caption);
		}
	}

	function endsWith(str, suffix) {
	    return str.indexOf(suffix, str.length - suffix.length) !== -1;
	}
});