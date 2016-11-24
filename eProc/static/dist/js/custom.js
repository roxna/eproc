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
		        console.log(data);
				
				var vendorCo = data[0]['fields'];
				$('#vendorContactRep').text(vendorCo['contact_rep']);
				$('#vendorID').text(vendorCo['vendorID']);
				$('#vendorComments').text(vendorCo['comments']);

		        var company = data[1]['fields'];		        
		        $('#vendorName').text(company['name']);
		        $('#vendorWebsite').text(company['website']);
		        

		        try{
		        	var location = data[3]['fields'];
		        }catch(error){

		        }
		    },
		    failure: function(data) { 
		        alert('Got an error dude');
		    }
		});


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
