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

		console.log(api_url);

		if (api_url.substring(0, 4) !== 'None') {
			$.getJSON(url=api_url,
				  callback=on_api_load);
		}
	}

	function on_api_load(data) {
		var photo_div = '<div class="col-sm-6 col-md-4 col-lg-3 photo-col"> \
	                    <div class="photo" style="display:none"> \
	                    	<a data-toggle="modal" href="#media-modal"> \
	                        <img src="{{img_src}}" class="img-responsive" data-igid="{{igid}}"> \
	                        </a> \
	                    </div> \
	                </div>';

	    var load_more_button = '<button class="btn btn-lg btn-primary" id="loadmore">Load more</button>'

		if (data.meta.code == 200) {
			console.log(data.data.length)
			// Insert photos
			for (i=0; i<data.data.length; i++) {
				photo = data.data[i];
				photos[photo.id] = photo;
				html_to_append = photo_div.replace('{{img_src}}',photo.images.low_resolution.url);
				html_to_append = html_to_append.replace('{{igid}}',photo.id);
				$('#media-holder').append(html_to_append);
			}

			// Fade in Photos
			$('.img-responsive').bind('load', function() { $(this).parent().parent().fadeIn('slow'); })

			// Launch Modals
			if (document.width > 768) {
				$('.img-responsive').bind('click', function() {
					load_modal.call(this);
				});				
			} else {
				$('.photo a').removeAttr('href').on('click', function() { return null; });
			}

			function load_modal(igid) {
				console.log('igid ' + igid);
				igid = typeof igid !== 'undefined' ? igid : $(this).attr('data-igid');
				$('#media-modal .modal-body').children().remove();

				var data_prev = $(this).closest('.photo-col').prev().find('img');
				var data_next = $(this).closest('.photo-col').next().find('img');
				data_prev_id = data_prev.length > 0 ? data_prev.attr('data-igid') : null;
				data_next_id = data_next.length > 0 ? data_next.attr('data-igid') : null;
				
				if (data_prev_id) {
					$('#media-modal .btn-prev i').show();
					$('#media-modal .btn-prev').off().on('click', function() {
						load_modal.call(data_prev, data_prev_id);
					});					
				} else {
					console.log('hide');
					$('#media-modal .btn-prev i').hide();
				}

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
	
			// Remove loading gif
			$('#ajax-loader').remove();
			$('#loadmore').removeClass('button-loading');

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
		} else {
			alert("Couldn't load data from Instagram. Please try again.");
		}
	}
});