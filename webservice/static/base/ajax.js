function Ajax() {
    'use strict';
}

(function() {
    'use strict';

    Ajax.prototype.request = function(path, attType, attData, onSuccess, onError) {
        console.log("Ajax.request");
        var self = this;
        onError = typeof onError !== 'undefined' ? onError : null;

        if (attType === "POST") {
            var csrftoken = this.getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!self.csrfSafeMethod(settings.type) && self.sameOrigin(settings.url)) {
                        // Send the token to same-origin, relative URLs only.
                        // Send the token only if the method warrants CSRF protection
                        // Using the CSRFToken value acquired earlier
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
        }

        $.ajax({
            url : "http://" + location.host + "/" + path,
            global : false,
            type : attType,
            data : attData,
            dataType : 'html',
            async : false,
            success : onSuccess,
            error : onError
        });
    };
    
    //TODO: transfer to some utils? cross-domain ajax not working , crsf cookie needed
    Ajax.prototype.getCookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    Ajax.prototype.csrfSafeMethod = function(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    Ajax.prototype.sameOrigin = function(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    };
}());

$(document).on("ready", function() {
    ajax = new Ajax();
});
