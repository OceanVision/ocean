function Ajax() {
    'use strict';
}

(function() {
    'use strict';

    Ajax.prototype = {
        pathsMap : {
            "ajax/sign_in" : "sign_in",
            "ajax/edit_profile" : "edit_profile",
            "ajax/rss" : "rss"
        }
    };

    Ajax.prototype.request = function(path, attType, attData, onSuccess, onError) {
        var self = this;
        onError = typeof onError !== 'undefined' ? onError : null;

        if (attType === "POST") {
            var csrftoken = utils.getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend : function(xhr, settings) {
                    if (!utils.csrfSafeMethod(settings.type) && utils.sameOrigin(settings.url)) {
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
            success : function(response) {
                onSuccess(response);
                window.history.pushState(
                    {page : "sign_in"},
                    "Sign in",
                    self.pathsMap[path]
                );
            },
            error : onError
        });
    };
}());
