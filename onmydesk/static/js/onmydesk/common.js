/* globals $ */

$(function(){
    function updateQueryStringParameter(uri, key, value) {
        var re, separator;

        re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
        separator = uri.indexOf('?') !== -1 ? "&" : "?";

        if (value == null) {
            if (uri.match(re)) {
                return uri.replace(re, '$1' + '$2');
            }
            else {
                return uri;
            }
        }
        else {
            if (uri.match(re)) {
                return uri.replace(re, '$1' + key + "=" + value + '$2');
            }
            else {
                return uri + separator + key + "=" + value;
            }
        }
    }

    $('#id_report').change(function(){
        var elem = $(this);

        if (elem.val()) {
            // Removing unload alert
            window.onbeforeunload = function(){};
            window.location = updateQueryStringParameter(
                window.location.href, 'report', elem.val());
        }
        else {
            // Removing unload alert
            window.onbeforeunload = function(){};
            window.location = updateQueryStringParameter(
                window.location.href, 'report', null);
        }
    });
});
