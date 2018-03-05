function load_dataset(){
    new Ajax.Request('/auto/ajax_color_request/', { 
    method: 'post',
    parameters: $H({'type':$('id_type').getValue()}),
    onSuccess: function(transport) {
        alert('warning');
        var e = $('id_color')
        if(transport.responseText)
            e.update(transport.responseText)
    }
    }); // end new Ajax.Request
}

