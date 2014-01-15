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
            "rss" : "/rss",
            "mission" : "/mission",
            "rss/news_preview" : "/rss/news_preview"
        }
    };

    Ajax.prototype.request = function(path, attType, attData, onSuccess, onError) {
        var pathParts = path.split('?');
        pathParts[1] = pathParts[1] != '' ? pathParts[1] + '&ajax=ok' : 'ajax=ok';
        onError = typeof onError !== 'undefined' ? onError :
                function(xhr, status, error) {
                    console.log(JSON.stringify(error));
                    console.log(JSON.stringify(status));
                    console.log(JSON.stringify(xhr));
                }
        ;

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
            url : "http://" + location.host + "/" + pathParts[0] + "?" + pathParts[1],
            global : false,
            type : attType,
            data : attData,
            dataType : 'html',
            async : false,
            success : function(response) {
                onSuccess(response);
                if (response != "fail" && ajax.pathsMap[pathParts[0]] != undefined) {
                    window.history.replaceState(
                        {page : path},
                        "Title",
                        ajax.pathsMap[pathParts[0]]
                    );
                }
            },
            error : onError
        });
    };
}());
