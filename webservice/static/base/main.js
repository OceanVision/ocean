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
	    ajax.request("user_profile/get_sign_in_form", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.showSignInForm($(response));
	};

    //under construction
    Main.prototype.showEditProfileForm = function() {
        var response = null;
	    ajax.request("user_profile/get_edit_profile_form", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.showSignInForm($(response));
    };

    Main.prototype.editProfile = function() {
        var data = {
            'current_password' : $("#currentPassword").val(),
            'new_password' : $("#newPassword").val(),
            'retyped_password' : $("#retypedPassword").val()
        };

        ajax.request("user_profile/edit_profile", "POST", data, function(response) {
	    console.log(response);
	    window.location.replace("");
        }, function(xhr, ajaxOptions, thrownError) {
            alert(JSON.stringify(thrownError));
            alert(JSON.stringify(ajaxOptions));
            alert(JSON.stringify(xhr));
        });
    };

    //under construction
    Main.prototype.showMyOcean = function() {
        var response = null;
	    ajax.request("rss/", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.showSignInForm($(response));
    };

	Main.prototype.signIn = function() {
	    var data = {
	        'username' : $("#username").val(),
	        'password' : $("#password").val() //$("Crypto.SHA256($("#password").val())
	    };

	    ajax.request("user_profile/sign_in", "POST", data, function(response) {
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
    ajax = new Ajax();
    visualization = new Visualization();
});
