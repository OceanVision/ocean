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
        $("body").children().each(function() {
            visualization.fadeIn($(this));
        });
    };

    Main.prototype.load = function(path) {
	    var response = null;
	    ajax.request(path, "GET", "", function(r) {
	        response = r;
	    }, function(xhr, status, error) {
	        console.log(status);
	    });

	    //TODO: not a good choice for every next case
	    visualization.transit($("body").children().not("#regularMenu"), $(response));
	};

    Main.prototype.editProfile = function() {
        var data = {
            'current_password' : $("#currentPassword").val(),
            'new_password' : $("#newPassword").val(),
            'retyped_password' : $("#retypedPassword").val()
        };

        ajax.request("user_profile/edit_profile", "POST", data, function(response) {
	        console.log(response);
	        //main.load("");
        }, function(xhr, status, error) {
            console.log(JSON.stringify(error));
            console.log(JSON.stringify(status));
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
	        main.load("rss");
        }, function(xhr, status, error) {
            console.log(JSON.stringify(error));
            console.log(JSON.stringify(status));
            console.log(JSON.stringify(xhr));
        });
	};
}());

$(document).on("ready", function() {
    utils = new Utils();
    visualization = new Visualization();
    main = new Main();
    ajax = new Ajax();
});
