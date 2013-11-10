function Visualization() {
    'use strict';
    this.init();
}

(function() {
    'use strict';

    Visualization.prototype = {
		state : {
			navigatorVisibility : false,
			signInColor : null
		},
		
		colors : ["00c6c5", "c500fe", "ff1701", "976834", "9c8c5b", 
		         "00a001", "7b00fe", "bc002c", "bc002c", "896fa1", 
		         "6fc41c", "005dfe", "fa0086", "ffbd0d", "74899d", 
		         "bee301", "1fbbfe", "ff84f2", "ff7901", "7e9c75"]
	};

    Visualization.prototype.init = function() {
        //sign in color
        var color = this.getRandomColor();
        this.addGlobalStyle(".menu .item.highlighted", "background-color", "#" + color);
        this.addGlobalStyle("#signInForm .submit", "background-color", "#" + color);
        this.addGlobalStyle("#editProfileForm .submit", "background-color", "#" + color);
		this.updateEventHandlers();
	};

	Visualization.prototype.getRandomColor = function() {
		return this.colors[Math.floor(Math.random() * 20)];
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
	    element.css("left", (($(window).width() - element.width()) / 2) + "px");
	    return this;
	};

	Visualization.prototype.centerVertically = function(element) {
	    element.css("top", (($(window).height() - element.height()) / 2) + "px");
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

    Visualization.prototype.transit = function(activeElement, newElement) {
        var delta, newElementLeft, activeElementEffects, newElementEffects;

        newElement
        .appendTo("body")
        .css("opacity", 0)
        .show();

        newElementLeft = activeElement.first().position().left
            + activeElement.first().width();

        newElement
        .filter("[data-transit='true']")
	    .offset({left : newElementLeft});

	    if (newElement.filter("[data-transit='true']").data("center_v")) {
            visualization.centerVertically(newElement.filter("[data-transit='true']"));
        }

	    delta = newElementLeft
	        - this.getCentralPosition(newElement.filter("[data-transit='true']")).left;
	    console.log(newElement.width());
        activeElementEffects = {
            "left" : "-=" + delta + "px",
            "opacity" : 0
        };
        newElementEffects = {
            "left" : "-=" + delta + "px",
            "opacity" : 1
        };

        this.updateEventHandlers();
        activeElement.animate(activeElementEffects, 300, function() {
            $(this).detach();
        });
        newElement.filter("[data-transit='true']").animate(newElementEffects, 650);
        newElement.filter("[data-transit!='true']").animate({"opacity" : 1}, 650);
        return this;
    };

    Visualization.prototype.updateEventHandlers = function() {
		// rss items colors and opening item
		$("#rssItems .item .title")
		.hover(function() {
		    $(this).css("background-color", "#" + $(this).data("color"));
			if ($(this).parent().find(".description:hidden").length == 1) {
				$(this).parent().css("border-bottom", "1px solid #fff");
			}
		}, function() {
		    $(this).css("background-color", "#fff");
			if ($(this).parent().find(".description:hidden").length == 1) {
				$(this).parent().css("border-bottom", "1px solid #f0f0f0");
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
			$(this).css("border-left", "5px solid " + color);
			
			$(this).hover(function() {
				$(this).css("background-color", color);
			}, function() {
				$(this).css("background-color", "#fff");
			});
		});

		// opening navigator
		$("#navigatorSwitcher")
		.off("click").on("click", function(e) {
			var animationSpeed = 400;
			e.stopImmediatePropagation();
			if (!visualization.state.navigatorVisibility) {
				$("#navigator").animate({
					left : "0px",
					opacity : "1"
				}, animationSpeed);
				
				$(this).animate({
					width : "30px",
					height : "30px",
					left : "170px",
					borderRadius : "15px"
				}, animationSpeed);
				
				visualization.state.navigatorVisibility = true;
			} else {
				$("#navigator").animate({
					left : "-130px",
					opacity : "0"
				}, animationSpeed);
				
				$(this).animate({
					width : "50px",
					height : "50px",
					left: "40px",
					borderRadius : "25px"
				}, animationSpeed);

				visualization.state.navigatorVisibility = false;
			}
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
