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
	    console.log("Main.signIn");
	    var data = {
	        username : $("#username").val(),
	        password : Crypto.SHA256($("#password").val())
	    };
	    alert($(ajax.request("rss/login", "POST", data)));
	};
}());

$(document).on("ready", function() {
    main = new Main();
});
