$(function() {


	// *** Create New Studio Form ***

	$(".chosen-select").chosen();

	// + symbol next to form fields
	$('.add-form-field').click(function() {
		// Clone the parent
		var parent_clone = $(this).parent().clone(true);

		var input_field = $(parent_clone).find('input');
		var select_field = $(parent_clone).find('select');

		var old_id = ''
		var new_id = ''
		var label_id = ''

		// Reset ID/name's in clone
		for (i = 0; i < input_field.length; i++) {
			// Get the old ID/name
			old_id = $(input_field[i]).attr('name').split('-')[0];

			// Create new ID/name, which will be oldid-N where N is number of fields in doc
			new_id = old_id + '-' + ($("input[name^='" + old_id.split('-')[0] + "']").length + 1);
			label_id = new_id;

			$(input_field[i]).removeAttr('id').attr('id',new_id);
			$(input_field[i]).removeAttr('name').attr('name',new_id);
		}

		for (i = 0; i < select_field.length; i++) {
			// Get the old ID/name
			old_id = $(select_field[i]).attr('name').split('-')[0];
			console.log('select_field[' + i + '] = ' + $(select_field[i]));
			console.log('old_id = ' + old_id);

			// Create new ID/name, which will be oldid-N where N is number of fields in doc
			new_id = old_id + '-' + ($("select[name^='" + old_id.split('-')[0] + "']").length + 1);

			$(select_field[i]).removeAttr('id').attr('id',new_id);
			$(select_field[i]).removeAttr('name').attr('name',new_id);
		}


		$(parent_clone).children('label').removeAttr('for').attr('for',label_id);

		// Add clone to doc
		$(this).parent().after(parent_clone)
		return false;
	});

	// Display different mailing address form
	$('#different-ma').click(function() {
		if ($('#different-ma input:checked').val() == 'yes') {
			$('#mailing_address').css('display','block');
			$('#ma_country_chosen').attr('style','width: 100%');
			$('#ma_subdivision_chosen').attr('style','width: 100%');
		} else {
			$('#mailing_address').css('display','none');
		}
	});

	// Subdivisions
	var enabled_countries = ['US', 'DE'];
	var subdivisions = {};
	subdivisions['DE'] = '<option value="DE-BW">Baden-Württemberg</option> \
						<option value="DE-BY">Bayern</option> \
						<option value="DE-BE">Berlin</option> \
						<option value="DE-BB">Brandenburg</option> \
						<option value="DE-HB">Bremen</option> \
						<option value="DE-HH">Hamburg</option> \
						<option value="DE-HE">Hessen</option> \
						<option value="DE-MV">Mecklenburg-Vorpommern</option> \
						<option value="DE-NI">Niedersachsen</option> \
						<option value="DE-NW">Nordrhein-Westfalen</option> \
						<option value="DE-RP">Rheinland-Pfalz</option> \
						<option value="DE-SL">Saarland</option> \
						<option value="DE-SN">Sachsen</option> \
						<option value="DE-ST">Sachsen-Anhalt</option> \
						<option value="DE-SH">Schleswig-Holstein</option> \
						<option value="DE-TH">Thüringen</option>';

	subdivisions['US'] = '<option value="US-AL">Alabama</option> \
						<option value="US-AK">Alaska</option> \
						<option value="US-AS">American Samoa</option> \
						<option value="US-AZ">Arizona</option> \
						<option value="US-AR">Arkansas</option> \
						<option value="US-CA">California</option> \
						<option value="US-CO">Colorado</option> \
						<option value="US-CT">Connecticut</option> \
						<option value="US-DE">Delaware</option> \
						<option value="US-DC">District of Columbia</option> \
						<option value="US-FL">Florida</option> \
						<option value="US-GA">Georgia</option> \
						<option value="US-GU">Guam</option> \
						<option value="US-HI">Hawaii</option> \
						<option value="US-ID">Idaho</option> \
						<option value="US-IL">Illinois</option> \
						<option value="US-IN">Indiana</option> \
						<option value="US-IA">Iowa</option> \
						<option value="US-KS">Kansas</option> \
						<option value="US-KY">Kentucky</option> \
						<option value="US-LA">Louisiana</option> \
						<option value="US-ME">Maine</option> \
						<option value="US-MD">Maryland</option> \
						<option value="US-MA">Massachusetts</option> \
						<option value="US-MI">Michigan</option> \
						<option value="US-MN">Minnesota</option> \
						<option value="US-MS">Mississippi</option> \
						<option value="US-MO">Missouri</option> \
						<option value="US-MT">Montana</option> \
						<option value="US-NE">Nebraska</option> \
						<option value="US-NV">Nevada</option> \
						<option value="US-NH">New Hampshire</option> \
						<option value="US-NJ">New Jersey</option> \
						<option value="US-NM">New Mexico</option> \
						<option value="US-NY">New York</option> \
						<option value="US-NC">North Carolina</option> \
						<option value="US-ND">North Dakota</option> \
						<option value="US-MP">Northern Mariana Islands</option> \
						<option value="US-OH">Ohio</option> \
						<option value="US-OK">Oklahoma</option> \
						<option value="US-OR">Oregon</option> \
						<option value="US-PA">Pennsylvania</option> \
						<option value="US-PR">Puerto Rico</option> \
						<option value="US-RI">Rhode Island</option> \
						<option value="US-SC">South Carolina</option> \
						<option value="US-SD">South Dakota</option> \
						<option value="US-TN">Tennessee</option> \
						<option value="US-TX">Texas</option> \
						<option value="US-UM">United States Minor Outlying Islands</option> \
						<option value="US-UT">Utah</option> \
						<option value="US-VT">Vermont</option> \
						<option value="US-VI">Virgin Islands, U.S.</option> \
						<option value="US-VA">Virginia</option> \
						<option value="US-WA">Washington</option> \
						<option value="US-WV">West Virginia</option> \
						<option value="US-WI">Wisconsin</option> \
						<option value="US-WY">Wyoming</option>';

	$('.country').bind('change load', function() {
		// Enables subdivision dropdown with country's subdivision
		var selected_country = $(this).val();
		var subdivision = $(this).closest('fieldset').find('.subdivisions');

		if ($.inArray(selected_country, enabled_countries) > -1) {
			subdivision.html(subdivisions[selected_country]);
			subdivision.removeAttr('disabled');
			subdivision.trigger('chosen:updated');
		} else {
			subdivision.html('<option>Country not supported yet</option>');
			subdivision.attr('disabled','disabled');
			subdivision.trigger('chosen:updated');
		}
	});
});