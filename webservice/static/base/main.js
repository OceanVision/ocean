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
               console.log(JSON.stringify(error));
                console.log(JSON.stringify(status));
                console.log(JSON.stringify(xhr));
	    });

	    //TODO: not a good choice for every next case
	    visualization.transit($("body").children().not("#regularMenu"), $(response));
	};

    Main.prototype.changePassword = function(currentPassword, newPassword, retypedPassword) {
        if (newPassword != retypedPassword) {
            return;
        }

        var returnValue, data = {
            'current_password' : currentPassword,
            'new_password' : newPassword
        };

        ajax.request("user_profile/change_password", "POST", data, function(response) {
	        if (response != "fail") {
	            main.load("rss");
                returnValue = true;
            } else {
                returnValue = false;
            }
        }, function(xhr, status, error) {
            console.log(JSON.stringify(error));
            console.log(JSON.stringify(status));
            console.log(JSON.stringify(xhr));
            returnValue = false;
        });

        return returnValue;
    };

	Main.prototype.signIn = function(username, password) {
	    var returnValue, data = {
	        'username' : username,
	        'password' : password //$("Crypto.SHA256($("#password").val())
	    };

	    ajax.request("user_profile/sign_in", "POST", data, function(response) {
            if (response != "fail") {
	            main.load("rss");
                returnValue = true;
            } else {
                returnValue = false;
            }
        }, function(xhr, status, error) {
            console.log(JSON.stringify(error));
            console.log(JSON.stringify(status));
            console.log(JSON.stringify(xhr));
            returnValue = false;
        });

        return returnValue;
	};

    Main.prototype.signOut = function() {
        var returnValue;
	    ajax.request("user_profile/sign_out", "GET", "", function(response) {
            main.load("");
            returnValue = true;
        }, function(xhr, status, error) {
            console.log(JSON.stringify(error));
            console.log(JSON.stringify(status));
            console.log(JSON.stringify(xhr));
            returnValue = false;
        });

        return returnValue;
	};

    Main.prototype.searchInTitles = function(pattern) {
        var titles = $("#rssItems div.item p.title");
        titles.each(function() {
            var text = $(this).text().toLowerCase();
            if (text.indexOf(pattern.toLowerCase()) >= 0) {
                $(this).parent().show();
            } else {
                $(this).parent().hide();
            }
        });
    };

    //Niewydajny ten sort troche, po co usuwać divy i tworzyc na nowo?
    //Chyba, ze i tak to bedzie przepisywane na sortowanie po stronie serwera?
    Main.prototype.sort = function(container, elements, order) {
        var array = [];
        elements.each(function() {
            array.push({
                title : $(this).find("p.title").text(),
                element : $(this)
            });
        });

        array.sort(function(a, b) {
            if (a.title < b.title) {
                return (order == "ascending" ? -1 : 1);
            }
            else if (a.title > b.title) {
                return (order == "ascending" ? 1 : -1);
            }
            return 0;
        });

        var sortedElements = $("<div></div>");
        for (var i = 0; i < array.length; ++i) {
            sortedElements.append(array[i].element);
        }

        container
            .remove("div.item")
            .append(sortedElements.find("div.item"));
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

    //TODO: Czemu to jest tutaj? Przeciez nie kazda strona jest scrollowalna w ten sposob jak ListDisplay ;p
    $(window).scroll(function() {
        buffer = 40 // # of pixels from bottom of scroll to fire your function. Minimum 40 (should work for 0
        if ($("#rssItems").prop('scrollHeight') - $(window).scrollTop() <= $(window).height() + buffer) {
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
