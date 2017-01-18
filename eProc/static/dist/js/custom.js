$(document).ready(function(){

	/********************************************
	**** REQ: ADD/DELETE ORDER ITEM DETAILS  ****
	********************************************/
	
	var prefix = 'order_items';
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
            // $(this).val('');
            console.log(this);
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


	/*******************************************
	****     NEW PURCHASE ORDER DETAILS      ***
	*******************************************/

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
	  	}else{
	  		$('#nextPage').prop('disabled', false);	
	  	}
	  		      	
	  	POSubTotal = 0;
	  	$('#POOrdersTable tbody').empty();
		$('#orderTable input[type="checkbox"]:checked').each(function(){
			// Update SUBTOTAL from list of order_items checked
			var itemSubTotal =  parseInt($(this).closest("tr").find('.itemSubTotal').text());
			POSubTotal += itemSubTotal;

			// Show Order Items on 2nd page
			$('#POOrdersTable tbody').append(
				'<tr>' +
					'<td>' + $(this).closest('tr').find('.itemName').text() + '</td>' +
					'<td>' + $(this).closest('tr').find('.itemQty').text() + '</td>' +
					'<td>' + $(this).closest('tr').find('.itemUnitPrice').text() + '</td>' +					
					'<td>' + $(this).closest('tr').find('.itemSubTotal').text() + '</td>' +
					'<td>' + $(this).closest('tr').find('.itemVendor').text() + '</td>' +
					// '<td>' + '<a href=""><i class="fa fa-pencil"></i></a>' + '</td>' +
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


	/***************************************
	****      INVOICE UPDATE PO AJAX     ***
	***************************************/
	// Dynamically updated the PO list based on Invoice selected on new_invoice

	$('#invoiceOrdersTable').hide();
    $("#id_purchase_order").attr("readonly", true);  // Note: jQuery 1.9+ --> .prop (not .attr)    

    $('#selectVendor').on('click', function(){             
        $("#id_vendor_co").attr("readonly", true);
        $("#id_purchase_order").attr("readonly", false);
        var vendor_id = $('#div_id_vendor_co #id_vendor_co').val();
        $.ajax({
            url: '/invoices/'+vendor_id,
            type: 'get',
            success: function(data){              
                $('select[id=id_purchase_order]').html('');
                $.each(data, function(key, value){
                    $('select[id=id_purchase_order]').append('<option value="' + this['pk'] + '">' + this['fields']['number'] +'</option>'); 
                });
            },
            error: function(data){
                console.log(data);
            }
        })
    })

    $('#selectPO').on('click', function(){ 
        var po_id = $('#id_purchase_order option:selected').val(); 
        $("#id_purchase_order").attr("readonly", true);
        $.ajax({
            url: '/purchase-order/items/'+po_id,
            type: 'get',
            success: function(data){
                $('#invoiceOrdersTable').show(); 
                $.each(data, function(key, value){                
                    $('#invoiceOrdersTable tbody').append(
                        '<tr>'+
                            '<td>'+this['product']+'</td>'+
                            '<td>'+this['quantity']+'</td>'+
                            '<td>'+this['unit_price']+'</td>'+
                            '<td>'+this['sub_total']+'</td>'+
                            '<td>'+this['comments']+'</td>'+
                        '<tr>'
                    );
                }); 
            },
            error: function(data){
                console.log(data);
            }
        })            
    })
	

})
