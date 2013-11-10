function Main() {
	'use strict';
	this.init();
}

(function() {
	'use strict';

	Main.prototype.init = function() {
	    this.loadInitialContent();
	};

	Main.prototype.loadInitialContent = function() {
        for (var i = 0; i < contentToLoad.length; ++i) {
            visualization.fadeIn(contentToLoad[i]);
        }
    };

    Main.prototype.load = function(path) {
	    var response = null;
	    ajax.request(path, "GET", "", function(r) {
	        response = r;
	    });

	    //TODO: not a good choice for every next case
	    visualization.transit($("body").children(), $(response));
	};

    // deprecated
	Main.prototype.showSignInForm = function() {
	    var response = null;
	    ajax.request("ajax/sign_in", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.transit($("body").children(), $(response));
	};

	// deprecated
    Main.prototype.showEditProfileForm = function() {
        var response = null;
	    ajax.request("ajax/edit_profile", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.transit($("body").children(), $(response));
    };

    // deprecated
    Main.prototype.showRSS = function() {
        var response = null;
	    ajax.request("ajax/rss", "GET", "", function(r) {
	        response = r;
	    });

	    visualization.transit($("body").children(), $(response));
    };

    Main.prototype.editProfile = function() {
        var data = {
            'current_password' : $("#currentPassword").val(),
            'new_password' : $("#newPassword").val(),
            'retyped_password' : $("#retypedPassword").val()
        };

        ajax.request("user_profile/edit_profile", "POST", data, function(response) {
	        console.log(response);
        }, function(xhr, ajaxOptions, thrownError) {
            console.log(JSON.stringify(thrownError));
            console.log(JSON.stringify(ajaxOptions));
            console.log(JSON.stringify(xhr));
        });
    };

	Main.prototype.signIn = function() {
	    var data = {
	        'username' : $("#username").val(),
	        'password' : $("#password").val() //$("Crypto.SHA256($("#password").val())
	    };

	    ajax.request("user_profile/sign_in", "POST", data, function(response) {
	        console.log(response);
	        main.load("ajax/rss");
        }, function(xhr, ajaxOptions, thrownError) {
            console.log(JSON.stringify(thrownError));
            console.log(JSON.stringify(ajaxOptions));
            console.log(JSON.stringify(xhr));
        });
	};
}());

$(document).on("ready", function() {
    visualization = new Visualization();
    main = new Main();
    utils = new Utils();
    ajax = new Ajax();
});

var contentToLoad = [];
