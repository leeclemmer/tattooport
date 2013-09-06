// Hide mobile address bar
window.addEventListener("load",function() {
	setTimeout(function(){
		window.scrollTo(0, 1);
	}, 0);
});

$(function() {
	$('.img-responsive').bind('load', function() { $(this).parent().fadeIn('slow'); })
	
	$.getJSON(url=$_API_URL,
			  callback=on_api_load);

	var photo_div = '<div class="col-sm-6 col-md-4 col-lg-3"> \
                    <div class="photo" style="display:none"> \
                        <img src="{{img_src}}" class="img-responsive"> \
                    </div> \
                </div>'

	function on_api_load(data) {
		if (data.meta.code == 200) {
			for (i=0; i<data.data.length; i++) {
				photo = data.data[i];
				html_to_append = photo_div.replace('{{img_src}}',photo.images.low_resolution.url)
				$('#media-holder').append(html_to_append);
			}

			$('#ajax-loader').remove();
		} else {
			alert("Couldn't load data from Instagram. Please try again.");
		}
	}
});