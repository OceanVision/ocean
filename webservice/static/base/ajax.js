function Ajax() {
    'use strict';
}

(function() {
    'use strict';

    Ajax.prototype.request = function(path, attType, attData) {
        console.log("Ajax.request");
        var response = null;
        attType = typeof attType !== 'undefined' ? attType : "GET";
        attData = typeof attData !== 'undefined' ? attData : "";

        $.ajax({
            url: "http://" + location.host + "/" + path,
            global: false,
            type: attType,
            data: attData,
            dataType: 'html',
            async: false,
            success: function(r) {
                response = r;
            }
        });
        return response;
    };

    Ajax.prototype.signIn = function() {
    
    };
}());

$(document).on("ready", function() {
    ajax = new Ajax();
});
