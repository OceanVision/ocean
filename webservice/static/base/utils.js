function Utils() {
    'use strict';
}

(function() {
    'use strict';

    Utils.prototype = {
        colors : ["00c6c5", "c500fe", "ff1701", "976834", "9c8c5b", 
		         "00a001", "7b00fe", "bc002c", "bc002c", "896fa1", 
		         "6fc41c", "005dfe", "fa0086", "ffbd0d", "74899d", 
		         "bee301", "1fbbfe", "ff84f2", "ff7901", "7e9c75"]
    };
    
    Utils.prototype.getRandomColor = function() {
		return this.colors[Math.floor(Math.random() * 20)];
	};

    /* ========== A J A X ========== */
    Utils.prototype.getCookie = function(name) {
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

    Utils.prototype.csrfSafeMethod = function(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    Utils.prototype.sameOrigin = function(url) {
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
