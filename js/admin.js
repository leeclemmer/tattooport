$(function() {
	// *** Create New Studio Form ***

	//## Init the chosen plugin dropdowns
	$(".chosen-select").chosen();

	//## + symbol next to form fields
	$('.add-form-field').click(function() {
		// Clone the parent
		var parent_clone = $(this).parent().clone(true);

		var input_field = $(parent_clone).find('input');
		var select_field = $(parent_clone).find('select');

		var old_id = ''
		var new_id = ''
		var label_id = ''

		function reset_clone(clone) {
			// Reset ID/name's in clone
			for (i = 0; i < clone.length; i++) {
				// Get the old ID/name
				old_id = $(clone[i]).attr('name').split('-')[0];

				// Create new ID/name, which will be oldid-N where N is number of fields in doc
				new_id = old_id + '-' + ($(clone.prop('tagName').split('_')[0] + "[name^='" + old_id.split('-')[0] + "']").length + 1);
				label_id = new_id;

				$(clone[i]).removeAttr('id').attr('id',new_id);
				$(clone[i]).removeAttr('name').attr('name',new_id);
				$(clone[i]).val('');
			}
		}
		
		reset_clone(input_field);
		reset_clone(select_field);

		$(parent_clone).children('label').removeAttr('for').attr('for',label_id);

		// Add clone to doc
		$(this).parent().after(parent_clone)
		return false;
	});


	//## Display different mailing address form
	var toggle_ma = function() {
		if ($('#different-ma input:checked').val() == 'yes') {
			$('#mailing_address').css('display','block');
			$('#ma_country_chosen').attr('style','width: 100%');
			$('#ma_subdivision_chosen').attr('style','width: 100%');
		} else {
			$('#mailing_address').css('display','none');
		}
	}; 

	$('#different-ma').click(toggle_ma);
	toggle_ma();


	//## Generate country dropdown
	function select_html(kv, selected) {
		// function generates <options> HTML given object kv where k = value and id and v is the text
		var html = '<options value=""></options>';
		for (var k in kv) {
			s = '';
			if (k == selected) s = ' selected';
			html += '<option value="' + k + '" id="' + k + '"' + s + '>' + kv[k] + '</option>\n';
		}
		return html;
	}
	
	// Put popular countries at top of list
	country_names = {};
	country_names['US'] = 'United States';
	country_names['DE'] = 'Germany';

	for (country_code in COUNTRIES) {
		country_names[country_code] = COUNTRIES[country_code]['name'];
	}

	// Populate address country field
	var html = select_html(country_names, $_LOC['country']);
	$('#country').html(html);
	$('#country').trigger('chosen:updated');

	// Populate mailing address country field
	html = '<option value=""></option>';
	html += select_html(country_names, $_LOC['ma_country']);
	$('#ma_country').html(html);
	$('#ma_country').trigger('chosen:updated'); 


	//## Generate subdivision drop downs				
	var generate_subdivisions = function() {
		// Enables subdivision dropdown with country's subdivision
		var selected_country = $(this).val();
		if (!selected_country) selected_country = 'US';

		var subdivision = $(this).closest('fieldset').find('.subdivisions');

		var selected = $_LOC['subdivision'];
		if ($(this).attr('id') == 'ma_country') selected = $_LOC['ma_subdivision'];

		var html = '<option value=""></option>';
		html += select_html(COUNTRIES[selected_country]['subdivisions'],selected);
		
		if ($.inArray(selected_country, ENABLED_COUNTRIES) > -1) {
			subdivision.html(html);
			subdivision.removeAttr('disabled');
			subdivision.trigger('chosen:updated');
		} else {
			subdivision.html('<option>Country not supported yet</option>');
			subdivision.attr('disabled','disabled');
			subdivision.trigger('chosen:updated');
		}			
	};

	// when select is refreshed
	$('.country').on('change', generate_subdivisions);

	// when doc is loaded
	generate_subdivisions.apply($('#country'));
	generate_subdivisions.apply($('#ma_country'));

	// Pressing key on artist create form
	$('#display_name').on('keyup', function(event) {
		// Autopopulate First and Last Name for artist
		$('#first_name').attr('value',this.value.split(' ')[0]);
		$('#last_name').attr('value',this.value.split(' ')[1]);

		set_helper_links.apply(this);
	});

	// Pressing key on artist create form
	$('#name').on('keyup', function() {
		set_helper_links.apply(this);
	});

	function set_helper_links() {
		// Autopopulates Google searches to cut down on typing time
		var google_search = "https://www.google.com/search?q=";
		var name = this.value + " tattoo";

		$('#website-label').attr('href',google_search + name);
		$('#instagram-label').attr('href',google_search + name + " instagram");
		$('#facebook-label').attr('href',google_search + name + " facebook");
		$('#twitter-label').attr('href',google_search + name + " twitter");
		$('#tumblr-label').attr('href',google_search + name + " tumblr");
		$('#foursquare-label').attr('href',google_search + name + " foursquare");
	}
});