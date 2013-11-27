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

    page = 0
    pageSize = 20

    function createNews(news, i) {
        var item = $("<div></div>")
            .appendTo("#rssItems")
            .attr("class", "item")
            .attr("title", news["category"])
            .attr("id", "news_" + ((page * pageSize) + i).toString());

        var span = $("<span></span>")
            .appendTo("#rssItems #news_" + ((page * pageSize) + i).toString())
            .attr("class", "no");

        var p1 = $("<p></p>")
            .appendTo("#news_" + ((page * pageSize) + i).toString())
            .attr("class", "title")
            .attr("data-color", news["color"])
            .attr("id", "p1_" + ((page * pageSize) + i).toString());
        id = "#rssItems #news_" + ((page * pageSize) + i).toString() + " #p1_" + ((page * pageSize) + i).toString()
        $(id).text(news["title"]);

        var p2 = $("<p></p>")
            .appendTo("#news_" + ((page * pageSize) + i).toString())
            .attr("class", "description")
            .attr("id", "p2_" + ((page * pageSize) + i).toString());
        id = "#rssItems #news_" + ((page * pageSize) + i).toString() + " #p2_" + ((page * pageSize) + i).toString()
        $(id).text(news["description"]);
    }

    $(window).scroll(function() {
        buffer = 40 // # of pixels from bottom of scroll to fire your function. Minimum 40 (should work for 0)
        if ($("#rssItems").prop('scrollHeight') - $("#rssItems").scrollTop() <= $("#rssItems").height() + buffer) {
            page += 1
            var data = {
                'page' : page.toString(),
                'page_size' : pageSize.toString()
            };
            ajax.request("rss/get_news", "GET", data, function(response) {
                response = JSON.parse(response)["rss_items"]
                if (response != null) {
                    for (var i = 0; i < response.length; i++) {
                        news = response[i]
                        createNews(news, i)
                    }
                }
            }, function(xhr, status, error) {
                console.log(JSON.stringify(error));
                console.log(JSON.stringify(status));
                console.log(JSON.stringify(xhr));
            });
        }
    });
});
