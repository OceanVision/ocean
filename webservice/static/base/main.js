//TODO: transfer to some utils? cross-domain ajax not working , crsf cookie needed
function getCookie(name) {
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
}
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
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
}
//end utils


function Main() {
	'use strict';
}




(function() {
	'use strict';
	
	Main.prototype.getRandomInteger = function(a, b) {
	    return Math.round(Math.random() * b) + a;
	};

	Main.prototype.showSignInForm = function() {
	    console.log("Main.showSignInForm");
	    visualization.showSignInForm($(ajax.request("sign_in_view")));
	};
	
	Main.prototype.signIn = function() {

        var csrftoken = getCookie('csrftoken');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {

                    // Send the token to same-origin, relative URLs only.
                    // Send the token only if the method warrants CSRF protection
                    // Using the CSRFToken value acquired earlier
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
	    console.log("Main.signIn");
	    var datavar = {
	        'username' : $("#username").val(),
	        'password' : $("#password").val() //$("Crypto.SHA256($("#password").val())
	    };

        $.ajax({
             type:"POST",
             url: "rss/login/",
             data: datavar,
             success:
                 function(response){
                     console.log(response);
                 },
            error:
                function(xhr, ajaxOptions, thrownError){
                    alert(JSON.stringify(thrownError));
                    alert(JSON.stringify(ajaxOptions));
                    alert(JSON.stringify(xhr));
                }
            }

         );

	};
}());

$(document).on("ready", function() {
    main = new Main();
});
