function Main() {
	'use strict';
}

(function() {
	'use strict';

	Main.prototype.getRandomInteger = function(a, b) {
	    return Math.round(Math.random() * b) + a;
	};

	Main.prototype.showSignInForm = function() {
	    var response = null;
	    ajax.request("get_sign_in_view", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.showSignInForm($(response));
	};

    //under construction
    Main.prototype.showEditProfileForm = function() {
        var response = null;
	    ajax.request("get_edit_profile_view", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.showSignInForm($(response));
    };

    //under construction
    Main.prototype.showMyOcean = function() {
        var response = null;
	    ajax.request("rss", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.showSignInForm($(response));
    };

	Main.prototype.signIn = function() {
        console.log("Main.signIn");
	    var data = {
	        'username' : $("#username").val(),
	        'password' : $("#password").val() //$("Crypto.SHA256($("#password").val())
	    };

	    ajax.request("rss/sign_in/", "POST", data, function(response) {
	        console.log(response);
	        window.location.replace("");
        }, function(xhr, ajaxOptions, thrownError) {
            alert(JSON.stringify(thrownError));
            alert(JSON.stringify(ajaxOptions));
            alert(JSON.stringify(xhr));
        });
	};
}());

$(document).on("ready", function() {
    main = new Main();
});
