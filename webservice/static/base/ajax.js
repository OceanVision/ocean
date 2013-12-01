function Ajax() {
    'use strict';
}

(function() {
    'use strict';

    Ajax.prototype = {
        pathsMap : {
            "" : "/",
            "sign_in" : "/sign_in",
            "edit_profile" : "/edit_profile",
            "rss" : "/rss"
        }
    };

    Ajax.prototype.request = function(path, attType, attData, onSuccess, onError) {
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
            url : "http://" + location.host + "/" + path + "?ajax=ok",
            global : false,
            type : attType,
            data : attData,
            dataType : 'html',
            async : false,
            success : function(response) {
                onSuccess(response);
                if (response != "fail" && ajax.pathsMap[path] != undefined) {
                    window.history.replaceState(
                        {page : path},
                        "Title",
                        ajax.pathsMap[path]
                    );
                }
            },
            error : onError
        });
    };
}());
