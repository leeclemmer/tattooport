$(function() {
	$('.add-form-field').click(function() {
		// Clone the parent
		var parent_clone = $(this).parent().clone(true);

		// Get the old ID/name
		var input_field = $(parent_clone).find('input');
		var old_id = input_field.attr('id');

		// Create new ID/name, which will be oldid-N where N is number of fields in doc
		var new_id = old_id + '-' + ($("input[name^='" + old_id.split('-')[0] + "']").length + 1);

		// Reset ID/name's in clone
		input_field.removeAttr('id').attr('id',new_id);
		input_field.removeAttr('name').attr('name',new_id);
		$(parent_clone).children('label').removeAttr('for').attr('for',new_id);

		console.log($(parent_clone).children('.col-lg-9 input'));
		// Add clone to doc
		$(this).parent().after(parent_clone)
		return false;
	})
});