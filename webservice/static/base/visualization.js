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
	    element.css("left", (($(window).width() - element.outerWidth()) / 2) + "px");
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
		$("#rssItems .item .title")
		.hover(function() {
		    $(this).css("background-color", "#" + $(this).data("color"));
			if ($(this).parent().find(".description:hidden").length == 1) {
				var color = utils.getDecimalColor($(this).data("color"));
				$(this).parent().css("border-bottom", "1px solid rgba(" + color[0] + ", "
                    + color[1] + ", " + color[2] + ", .2)");
			}
		}, function() {
		    $(this).css("background-color", "transparent");
			if ($(this).parent().find(".description:hidden").length == 1) {
                var color = utils.getDecimalColor($(this).data("color"));
				$(this).parent().css("border-bottom", "1px solid rgba(" + color[0] + ", "
                    + color[1] + ", " + color[2] + ", .2)");
			}
		})
		.off("click").on("click", function(e) {
		    e.stopImmediatePropagation();
			if($(this).parent().find(".description:hidden").length == 1) {
				$(this).parent().find(".description").show(200);
				$(this).css("font-weight", "bold");
			} else {
				$(this).parent().find(".description").hide(100);
				$(this).css("font-weight", "normal");
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
	};
}());
