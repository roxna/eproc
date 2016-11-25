$(document).ready(function(){
  	
	/***************************************
	****      VENDOR DETAILS AJAX       ***
	***************************************/	

	$('#vendorTable tbody tr td').on('click', function(vendors_json){
	    $('#noVendorSelected').hide();
	    $('#vendorDetailSection').show();

	    var id = parseInt($(this).data('id'));
	    var name = $(this).data('name');
	    console.log(id);
	    console.log(name);
	    $.ajax({
		    url: '/vendor/'+id+'/'+name,
		    type: 'get',
		    success: function(data) {
				var vendorCo = data[0]['fields'];
				$('#vendorContactRep').text(vendorCo['contact_rep']);
				$('#vendorID').text(vendorCo['vendorID']);
				$('#vendorComments').text(vendorCo['comments']);

		        var company = data[1]['fields'];		        
		        $('#vendorName').text(company['name']);
		        $('#vendorWebsite').text(company['website']);		        

		        try{
		        	var location = data[2]['fields'];
		        	$('#vendorEmail').text(location['email']);
		        	$('#vendorPhone').text(location['phone']);
		        	$('#vendorFax').text(location['fax']);
		        	$('#vendorAdd1').text(location['address1']);
		        	$('#vendorAdd2').text(location['address2']);
		        	$('#vendorCity').text(location['city']);
		        	$('#vendorState').text(location['state'].toUpperCase());
		        	$('#vendorZip').text(location['zipcode']);
		        	$('#vendorCountry').text(location['country'].toUpperCase());
		        }catch(error){

		        }
		    },
		    failure: function(data) { 
		        alert('Got an error dude');
		    }
		});
	});

	/********************************************
	**** REQ: ADD/DELETE ORDER ITEM DETAILS  ****
	********************************************/

	function updateElementIndex(el, prefix, ndx) {
	    var id_regex = new RegExp('(' + prefix + '-\\d+-)');
	    var replacement = prefix + '-' + ndx + '-';
	    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex,
	    replacement));
	    if (el.id) el.id = el.id.replace(id_regex, replacement);
	    if (el.name) el.name = el.name.replace(id_regex, replacement);
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

	function addForm(btn, prefix) {
	    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        // Clone a form (w/o event handlers) from 1st form & insert it after last form
        var row = $(".item:first").clone(false).get(0);
        $(row).removeAttr('id').hide().insertAfter(".item:last").slideDown(300);

        // Remove the bits we don't want in the new row/form e.g. error messages
        $(".errorlist", row).remove();
        $(row).children().removeClass("error");

        // Relabel or rename all the relevant bits
        $(row).children().children().each(function () {
            updateElementIndex(this, prefix, formCount);
            $(this).val("");
        });

        // Add an event handler for the delete item/form link 
        $(row).find(".delete").click(function () {
            return deleteForm(this, prefix);
        });
        // Update the total form count
        $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);
	}

	// Register the click event handlers
	$("#add").click(function () {
	    return addForm(this, "order_items");
	});

	$(".delete").click(function () {
	    return deleteForm(this, "order_items");
	});


	/***************************************
	****     PURCHASE ORDER DETAILS      ***
	***************************************/

	// Show/hide content as 1st/2nd page of PO Creation Form 
		$('#page2').hide();
		$('#prevPage').hide();
		$('.navigation').on('click', function(){
		$('.pages').toggle();
		$('.navigation').toggle();
	});

	// Set up
	var POSubTotal, POTotal;	
		$('#nextPage').prop('disabled', true);

		$( "form input:checkbox" ).change(function() {

		 	// Disable/Enable 'Add Items' step based on if items are selected
		if(!$('input[type="checkbox"]').is(':checked')){
	  		$('#nextPage').prop('disabled', true);
	  	}
	  	else{
	  		$('#nextPage').prop('disabled', false);	
	  	}
	  		      	
	  	POSubTotal = 0;
	  	$('#orderPOTable tbody').empty();
		$('#orderTable input[type="checkbox"]:checked').each(function(){

			// Update SUBTOTAL from list of order_items checked
			var itemSubTotal =  parseInt($(this).closest("tr").find('.itemSubTotal').text());
			POSubTotal += itemSubTotal;

			// Show Order Items on 2nd page
			$('#orderPOTable tbody').append(
				'<tr>' +
					'<td>' + $(this).closest("tr").find('.itemName').text() + '</td>' +
					'<td>' + $(this).closest("tr").find('.itemVendor').text() + '</td>' +
					'<td>' + $(this).closest("tr").find('.itemSubTotal').text() + '</td>' +				    
				'</tr>'
			)

		});
		$('#POSubTotal').html(POSubTotal);
		POTotal = POSubTotal;
		$('#POTotal').html(POTotal);

	});

	// Update GRAND TOTAL from costs and sub_total       
	$('#POTable').keyup(function(){    	
		POTotal = POSubTotal;
		$('#POTotal').html(POTotal);

	    $('td.amount').each(function() {
	    	// If cost, add; if discount, subtract
	    	$(this).hasClass('discount') ? POTotal -= parseInt($(this).children().val()) : POTotal += parseInt($(this).children().val());		        
	    });		     
	    $('#POTotal').html(POTotal);
	});

})
