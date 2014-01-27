function Visualization() {
    'use strict';
    this.init();
}

(function() {
    'use strict';

    Visualization.prototype = {
		state : {
			navigatorVisibility : false
		}
	};

    Visualization.prototype.init = function() {
        //sign in color
        var color = utils.getRandomColor();
        this.addGlobalStyle(".menu .item.highlighted", "background-color", "#" + color);
        this.addGlobalStyle("#signInForm .submit", "background-color", "#" + color);
        this.addGlobalStyle("#editProfileForm .submit", "background-color", "#" + color);
		this.updateEventHandlers();
	};

	Visualization.prototype.addGlobalStyle = function(element, attribute, value) {
	    var style = $('<style type="text/css">' + element + ' { ' + attribute 
	        + ': ' + value + ' !important; }</style>');
	    $("head").append(style);
	    return this;
	};

	Visualization.prototype.getCentralPosition = function(element) {
	    return {
	        left : ($(window).width() - element.width()) / 2,
	        top : ($(window).height() - element.height()) / 2
	    };
	};

	Visualization.prototype.centerHorizontally = function(element) {
	    element.css("left", ((element.parent().width() - element.outerWidth()) / 2) + "px");
	    return this;
	};

	Visualization.prototype.centerVertically = function(element) {
	    element.css("top", (($(window).height() - element.outerHeight()) / 2) + "px");
	    return this;
	};

	Visualization.prototype.fadeIn = function(element) {
	    if (element.data("center_h")) {
            visualization.centerHorizontally(element);
        }

        if (element.data("center_v")) {
            visualization.centerVertically(element);
        }

	    setTimeout(element.fadeIn.bind(element, 700), 500);
	    this.updateEventHandlers();
	    return this;
	};

    Visualization.prototype.transit = function(activeElements, newElements) {
        var delta, newElementsLeft, activeElementsEffects, newElementsEffects;

        newElements
            .appendTo("body")
            .css("opacity", 0)
            .show();

        newElementsLeft = activeElements.filter("[data-transit='true']").first().position().left
            + activeElements.filter("[data-transit='true']").first().width();

        newElements
            .filter("[data-transit='true']")
            .offset({left : newElementsLeft});

	    if (newElements.filter("[data-transit='true']").data("center_v")) {
            visualization.centerVertically(newElements.filter("[data-transit='true']"));
        }

	    delta = newElementsLeft
	        - this.getCentralPosition(newElements.filter("[data-transit='true']")).left;

        activeElementsEffects = {
            "left" : "-=" + delta + "px",
            "opacity" : 0
        };
        newElementsEffects = {
            "left" : "-=" + delta + "px",
            "opacity" : 1
        };

        this.updateEventHandlers();
        activeElements
            .filter("[data-transit='true']")
            .animate(activeElementsEffects, 300, function() {
                $(this).detach();
            });

        activeElements
            .filter("[data-transit!='true']")
            .animate({"opacity" : 0}, 300, function() {
                $(this).detach();
            });

        newElements.filter("[data-transit='true']").animate(newElementsEffects, 650);
        newElements.filter("[data-transit!='true']").animate({"opacity" : 1}, 650);
        return this;
    };

    Visualization.prototype.toggleNavigator = function() {
        var animationSpeed = 400;
		if (!this.state.navigatorVisibility) {
			$("#navigator").animate({
				left : "0px",
				opacity : "1"
			}, animationSpeed);

			$("#navigatorSwitcher").animate({
				width : "30px",
				height : "30px",
				left : "170px",
				borderRadius : "15px"
			}, animationSpeed);

			this.state.navigatorVisibility = true;
		} else {
			$("#navigator").animate({
				left : "-130px",
				opacity : "0"
			}, animationSpeed);

			$("#navigatorSwitcher").animate({
				width : "50px",
				height : "50px",
				left: "40px",
				borderRadius : "25px"
			}, animationSpeed);

			this.state.navigatorVisibility = false;
		}
    };

    Visualization.prototype.updateEventHandlers = function() {
		// rss items colors and opening item

		$("#rssItems .love_it_button").css({opacity:0.5});

		$("#rssItems .item .title")
            .css("background-color", function() {
                return utils.getRGBA($(this).data("color"), .05);
            })
            .hover(function() {
                $(this)
                    .css("background-color", "#" + $(this).data("color"))
                    .addClass("hover");
            }, function() {
                if($(this).parent().find(".description:hidden").length == 1) {
                    $(this)
                        .css("background-color", utils.getRGBA($(this).data("color"), .05))
                        .removeClass("hover");
                }
            })
            .off("click").on("click", function(e) {
                e.stopImmediatePropagation();
                if($(this).parent().find(".description:hidden").length == 1) {
                    $(this).parent().find(".description")
                        .show(200)
                        .css("border-bottom", "5px solid " + utils.getRGBA($(this).data("color"), .05));
                    $(this).addClass("selected");
                } else {
                    $(this).parent().find(".description").hide(100);
                    $(this).removeClass("selected");
                }
            });

		// navigator categories colors
		$("#navigator .item.category")
            .each(function() {
                var color = $(this).data("color");
                $(this).css("border-left", "6px solid " + color);

                $(this).hover(function() {
                    $(this).css("background-color", color);
                }, function() {
                    $(this).css("background-color", "transparent");
                });
            });

		// input focus/blur
		$("input")
            .off("focus").on("focus", function() {
                var el = $(this);
                if (!el.hasClass("focus") && el.val() == el.data("value")) {
                    el.val("").addClass("focus");

                    if(el.data("type") == "password") {
                        el.attr("type", "password");
                    }
                }
            })
            .off("blur").on("blur", function() {
                var el = $(this);
                if (el.hasClass("focus") && el.val() == "") {
                    el.val(el.data("value")).removeClass("focus");

                    if(el.data("type") == "password") {
                        el.attr("type", "text");
                    }
                }
            });

 // love buttons
                    //Love button
       // workaround:
       if ($(".love_it_image").data('qtip')) {
            $(".love_it_image").qtip(
                {
                show: {
                    delay: 1000
                },
                content: function(){
                    var data = {
                        'uuid' : $(this).attr("news_uuid")
                    };

                    var list = []

                    ajax.request("rss/get_loved_it_list", "GET", data, function(response) {
                        list=JSON.parse(response);
                     });

                    if(list.length==0) return "Love it button";
                     return list.join("\n");
                }}
            );
      // workaround:
      }
            $("#rssItems .love_it_button").off("click").on("click", function(e){
                    var data = {
                        'uuid' : $(this).attr("news_uuid")
                    };
                    var news_item = $("#rssItems .item[news_uuid="+data.uuid+"]")
                    var love_it_button = news_item.find(".love_it_button")


                    var current_state = love_it_button.children("img").attr("src")

                    if(current_state == heart){
                        ajax.request("rss/loved_it", "GET", data, function(response) {
                            var value = parseInt(news_item.find(".loved_counter").text())
                            news_item.find(".loved_counter").text(value + 1)
                            news_item.find(".love_it_image").attr("src", grayheart);
                        });

                    }else{

                        ajax.request("rss/unloved_it", "GET", data, function(response) {
                            var value = parseInt(news_item.find(".loved_counter").text())
                            news_item.find(".loved_counter").text(value - 1)
                            news_item.find(".love_it_image").attr("src", heart);
                        });


                    }

                    e.preventDefault();
             });



	};
}());
