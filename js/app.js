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

		/*if (document.width < 768) {
			// Smartphones
			api_url = api_url.replace(/count=../,'count=12');
		} else if (document.width >= 768 && document.width < 1200) {
			// Tablet
			api_url = api_url.replace(/count=../,'count=20');
		}*/

		if (api_url.substring(0, 4) !== 'None') {
			$.getJSON(url=api_url,
				  callback=on_api_load);
		}
	}

	function on_api_load(data) {
		var photo_div = '<div class="col-sm-6 col-md-4 col-lg-3 photo-col"> \
	                    <div class="photo" style="display:none"> \
	                    	<a data-toggle="modal" href="#media-modal"> \
	                        <img data-original="{{img_src}}" src="/img/1x1_2a2a2a.gif" class="img-responsive lazy" data-igid="{{igid}}" width="100%" height="auto"> \
	                        </a> \
	                    </div> \
	                </div>';

		if (data.meta.code == 200) {
			// Insert photos
			for (i=0; i<data.data.length; i++) {
				photo = data.data[i];
				photos[photo.id] = photo;
				
				html_to_append = photo_div.replace('{{img_src}}',photo.images.low_resolution.url);
				html_to_append = html_to_append.replace('{{igid}}',photo.id);
				
				$('#media-holder').append(html_to_append);
			}

			// Remove loading gif
			$('#ajax-loader').remove();
			$('#loadmore').removeClass('button-loading');

			// Bindings
			bind_photo_actions(data);
		} else {
			alert("Couldn't load data from Instagram. Please try again.");
		}
	}

	function bind_photo_actions(data) {				
		// Fade in Photos
		$('#media-holder img').bind('load', function() { $(this).parent().parent().fadeIn('slow'); });
		$('#media-holder img:last').parent().parent().fadeIn('slow');

		$('#media-holder img.lazy').lazyload({
			effect : "fadeIn",
			threshold : 600
		});

		// *** Insert Load button binding
		function insert_load_button() {
			// Insert load more button
			if (data.pagination.next_url) {
				if ($('#loadmore').length == 0) {
					$(load_more_button).insertAfter('#media-holder');
				};
				$('#loadmore').off().on('click', function() {
					$(this).addClass('button-loading');
					call_api(api_url=data.pagination.next_url + '&callback=?');
				});
			} else {
				$('#loadmore').remove()
			}
		}

		var load_more_button = '<button class="btn btn-lg btn-primary" id="loadmore">Load more</button>'
		
		$('#media-holder img:last').off().on('load', function() { insert_load_button() });


		// *** Launch Modal Bindings
		if (document.width >= 768) {
			// only bind for tablet or larger
			$('.img-responsive').bind('click', function() {
				load_modal.call(this);
			});
		} else {
			$('.photo a').removeAttr('href').on('click', function() { return null; });
		}

		function load_modal(igid) {
			igid = typeof igid !== 'undefined' ? igid : $(this).attr('data-igid');
			
			$('#media-modal .modal-body').children().remove();

			// Get previous and next image
			var data_prev = $(this).closest('.photo-col').prev().find('img');
			var data_next = $(this).closest('.photo-col').next().find('img');
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
									 src="' + photos[igid].caption.from.profile_picture + '"> ' + 
								photos[igid].caption.from.username + ' \
							</div>';

			modal_like_count = '<div class="likes-count"><i class="icon-heart"></i> ' + photos[igid].likes.count + '</div>';

			modal_comment_count = '<div class="comment-count"><i class="icon-comment"></i> ' + photos[igid].comments.count + '</div>';

			modal_caption = '<div class="caption">' + photos[igid].caption.text + '</div>';

			$('#media-modal .modal-meta').append(modal_author).append(modal_like_count).append(modal_comment_count).append(modal_caption);
		}
	}
});