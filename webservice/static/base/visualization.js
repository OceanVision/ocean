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
		
		colors: ["00c6c4", "c500ff", "ff1700", "976833", "9c8c5a", 
		         "00a000", "7b00ff", "bc002b", "bc002b", "896fa0", 
		         "6fc41b", "005dff", "fa0085", "ffbd0c", "74899c", 
		         "bee300", "1fbbff", "ff84f1", "ff7900", "7e9c74"]
	};
    
    Visualization.prototype.init = function() {
		console.log("Visualization.init");
		this.addEvents();
	};
	
	Visualization.prototype.getRandomColor = function() {
		return this.colors[Math.floor(Math.random() * 20)];
	};
	
	// TODO: more generic showing methods
	Visualization.prototype.showSignInForm = function(signInForm) {
	    signInForm
	        .appendTo("body")
	        .css({
	            "left" : ($(".menu").position().left + $(".menu").width()) + "px",
	            "top" : (($(window).height() - signInForm.height()) / 2 * 0.6) + "px",
	            "opacity" : 0
	        });
	        
	    signInForm
	        .find(".submit")
	        .css("background-color", "#" + visualization.state.signInColor);
	        
	    signInForm
	        .find("input")
	        .on("focus", function() {
	            var el = $(this);
	            if (!el.hasClass("focus") && el.val() == el.data("value")) {
	                el.val("")
	                    .addClass("focus");

	                if(el.data("type") == "password") {
	                    el.attr("type", "password");
	                }
	            }
	        })
	        .on("blur", function() {
	            var el = $(this);
	            if (el.hasClass("focus") && el.val() == "") {
	                el.val(el.data("value"))
	                    .removeClass("focus");

	                if(el.data("type") == "password") {
	                    el.attr("type", "text");
	                }
	            }
	        });

	    this.transition($("#bigBanner, .menu"), signInForm);
	};
    
    Visualization.prototype.transition = function(leftEl, rightEl) {
        console.log("Visualization.transition");
        var delta = rightEl.position().left - ($(window).width() - rightEl.width()) / 2,
        effectsLeft = {
            "left" : "-=" + delta + "px",
            "opacity" : 0
        }, effectsRight = {
            "left" : "-=" + delta + "px",
            "opacity" : 1
        };
        leftEl.animate(effectsLeft, 300);
        rightEl.animate(effectsRight, 700);
    };
    
    Visualization.prototype.addEvents = function() {
		var self = this;
		
		// sign_in item color
		$(".menu .item.highlighted").each(function() {
		    self.state.signInColor = self.getRandomColor();
			$(this).css("background-color", "#" + self.state.signInColor);
		});
		
		// rss items colors and opening item
		$(".content .item .title")
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
		.on("click", function(e) {
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
		$("#navigator .item.category").each(function() {
			var color = $(this).data("color");
			$(this).css("border-left", "5px solid " + color);
			
			$(this).hover(function() {
				$(this).css("background-color", color);
			}, function() {
				$(this).css("background-color", "#fff");
			});
		});
		
		// opening navigator
		$("#navigatorSwitcher").on("click", function(e) {
			var animationSpeed = 400;
			e.stopImmediatePropagation();
			if (!self.state.navigatorVisibility) {
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
				
				self.state.navigatorVisibility = true;
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

				self.state.navigatorVisibility = false;
			}
		});
	};
}());
