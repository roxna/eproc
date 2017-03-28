$(document).ready(function(){   
    
    // Make sure new_po/invoice_confirm page is entirely loaded first
    $(window).load(function() { 

    /*******************************************************
	****  NEW PO/INVOICE/DEBIT NOTE - UPDATE SUBTOTALS   ***
	*******************************************************/   

    /**************
    UPDATE TOTALS Function
    **************/
    // Function to update SUB TOTAL from qty & price
    var updateSubTotal = function(){
        SubTotal = 0;
        // Multiply price and quantity for each item row
        $('.item').each(function(){         

            if (window.location.pathname.includes('purchase-orders') || window.location.pathname.includes('debit_notes')){                
                var qty = $(this).find('.quantity').find('input').val();
                var price = $(this).find('.unit_price').find('input').val();
                SubTotal += qty * price;
            } else if (window.location.pathname.includes('invoices')){
                // If qty/price are not defined - it is on the new_INVOICE_confirm page because the values are texts
                var qty = $(this).find('.quantity').text();
                var price = $(this).find('.unit_price').text();
                SubTotal += qty * price;
            }

        });

        $('#subTotal').html(SubTotal);

    };      
    
    // Function to update GRAND TOTAL from costs and sub_total
    var updateGrandTotal = function(){
        GrandTotal = SubTotal;

        $('td.amount').each(function() {
            // If cost, add; if discount, subtract
            var amount = parseInt($(this).children().val());
            if (!isNaN(amount)){
                $(this).hasClass('discount') ? GrandTotal -= amount : GrandTotal += amount;
            }
        });
        $('#grandTotal').html(GrandTotal);

        // Disable Submit button if Grandtotal is negative
        if (GrandTotal < 0){
            $('#create').prop('disabled', true);
        }
    };

    /************** 
     Call UPDATE TOTALS on KEYUP
    **************/
    // SubTotal - on change in price or quantity
    $('.quantity, .unit_price, .subtotal').keyup(function(){
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

    // $('#subTotal').prop('readonly', true);
    // $('#grandTotal').prop('readonly', true);
    updateSubTotal();
    updateGrandTotal();

    });
});