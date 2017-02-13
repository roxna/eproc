$(document).ready(function(){   
    
    // Make sure new_po/invoice_confirm page is entirely loaded first
    $(window).load(function() { 

    /********************************************
	****  NEW PO/INVOICE - UPDATE SUBTOTALS   ***
	*********************************************/   

    /**************
    UPDATE TOTALS Function
    **************/
    // Function to update SUB TOTAL from qty & price
    var updateSubTotal = function(){
        SubTotal = 0;
        // Multiply price and quantity for each item row
        $('.item').each(function(){ 
            
            // If qty/price are defined - it is on the new_PO_confirm page because the values are inputs
            var qty = $(this).find('.quantity').find('input').val();
            var price = $(this).find('.unit_price').find('input').val();            

            // If qty/price are undefined - it is on the new_INVOICE_confirm page because the values are NOT inputs
            if (qty == undefined || price == undefined){
                var qty = $(this).find('.quantity').text();
                var price = $(this).find('.unit_price').text();
            }

            SubTotal += qty * price;
        });
        $('#subTotal :input').val(SubTotal);

    };      
    
    // Function to update GRAND TOTAL from costs and sub_total
    var updateGrandTotal = function(){
        GrandTotal = SubTotal;
        $('#grandTotal').html(GrandTotal);

        $('td.amount').each(function() {
            // If cost, add; if discount, subtract
            $(this).hasClass('discount') ? GrandTotal -= parseInt($(this).children().val()) : GrandTotal += parseInt($(this).children().val());               
        });
        $('#grandTotal').html(GrandTotal);
    };

    /************** 
     Call UPDATE TOTALS on KEYUP
    **************/
    // SubTotal - on change in price or quantity
    $('.quantity, .unit_price').keyup(function(){
        updateSubTotal();           
    });

    // Grand Total - on change in price/qty OR costs
    $('td, .item').keyup(function(){  
        updateGrandTotal();
    });

    /************** 
     SETUP
     **************/        
    var SubTotal = 0; 
    var GrandTotal = 0;   

    $('#subTotal :input').prop('readonly', true);
    // $('#grandTotal :input').prop('readonly', true);
    updateSubTotal();
    updateGrandTotal();

    });
});