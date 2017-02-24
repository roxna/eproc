$(document).ready(function(){

	/********************************************
	**** REQ: ADD/DELETE ORDER ITEM DETAILS  ****
	********************************************/
	
	// Set global variables
	// Set prefix based on formset name: 
	if (window.location.pathname.includes('requisitions') || window.location.pathname.includes('drawdown')){
		var prefix = 'items';  // new_req or new_dd
	} else{		
		var prefix = 'form'; // unbilled_items
	}	
	
	var id_regex = new RegExp('(' + prefix + '-\\d+)');

	// Register the click event handlers
	$("#add").click(function () {
		return addForm(this, prefix);
	});

	$(".delete").click(function () {
		return deleteForm(this, prefix);
	});	

	function addForm(btn, prefix) {
	    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
	    
        // Clone a form (w/o event handlers) from 1st form row & insert it after last form row
        var row = $(".item:first").clone(false).get(0);	
        $(row).find(':input').val('');
        row = $(row).attr('id', $(row).attr('id').replace(id_regex, prefix+'-'+formCount));
        
        $(row).hide().insertAfter(".item:last").slideDown(300);

        // Update the total form count
        $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);

        // Add an event handler for the delete item/form link
        $(row).find(".delete").click(function () {        	
            return deleteForm(this, prefix);
        });
        
        // Remove the bits we don't want in the new row/form e.g. error messages
        $(".errorlist", row).remove();
        $(row).children().removeClass("error");

        // Relabel or rename all the relevant bits of the new row
        $(row).children().children().each(function () {
            updateElementIndex(this, prefix, formCount);
            $(this).attr('value', '');
        });
	}	

	function updateElementIndex(el, prefix, ndx) {
	    var replacement = prefix + '-' + ndx;	    
		
		// Update the id/name/for values for each bit of the new row 
	    $(el).find('[id]').attr('id', $(el).find('[id]').attr('id').replace(id_regex, replacement));
	    $(el).find('label').attr('for', $(el).find('label').attr('for').replace(id_regex, replacement));
	    $(el).find('[name]').attr('name', $(el).find('[name]').attr('name').replace(id_regex, replacement));
	}

	function deleteForm(btn, prefix) {
	    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
	    if (formCount > 1) {	 
	        $(btn).parents('.item').remove(); // Delete the item/form 
	        var forms = $('.item'); // Get all the forms  
	        
	        // Update the total number of forms (1 less than before)
	        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
	        var i = 0;

	        // Go through the forms and set their indices, names and IDs
	        for (formCount = forms.length; i < formCount; i++) {
	            $(forms.get(i)).children().children().each(function () {
	                if ($(this).attr('type') == 'text') updateElementIndex(this, prefix, i);
	            });
	        }
	    }
	    return false;
	}	
	

})
