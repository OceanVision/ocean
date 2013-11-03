function Main() {
	'use strict';
	this.init();
}

(function() {
	'use strict';
	Main.prototype = {
		state : {
			navigatorVisibility: false
		},
		
		colors: ["00c6c4", "c500ff", "ff1700", "976833", "9c8c5a", 
		         "00a000", "7b00ff", "bc002b", "bc002b", "896fa0", 
		         "6fc41b", "005dff", "fa0085", "ffbd0c", "74899c", 
		         "bee300", "1fbbff", "ff84f1", "ff7900", "7e9c74"]
	};
	
	Main.prototype.init = function() {
		console.log("Main init()");
		this.addEvents();
	};
	
	Main.prototype.getRandomInteger = function(a, b) {
	    return Math.round(Math.random() * b) + a;
	};

	Main.prototype.getRandomColor = function() {
		return this.colors[Math.floor(Math.random() * 20)];
	};
	
	Main.prototype.addEvents = function() {
		var self = this;
		
		// kolor dla sign in
		$("#menu .item.highlighted").each(function() {
			$(this).css("background-color", "#" + self.getRandomColor());
		});
		
		// ukrywanie krawędzi przy rozwijaniu
		$("#content .item")
		.find(".title")
		.hover(function() {
			if ($(this).parent().find(".description:hidden").length == 1) {
				$(this).parent().css("border-bottom", "1px solid #fff");
			}
		}, function() {
			if ($(this).parent().find(".description:hidden").length == 1) {
				$(this).parent().css("border-bottom", "1px solid #f0f0f0");
			}
		});
		
		// kolory dla kategorii w nawigatorze
		$("#navigator .item.category").each(function() {
			var color = $(this).data("color");
			$(this).css("border-left", "5px solid " + color);
			
			$(this).hover(function() {
				$(this).css("background-color", color);
			}, function() {
				$(this).css("background-color", "#fff");
			});
		});
		
		// otwieranie nawigatora
		$("#navigatorSwitcher").on("click", function() {
			var animationSpeed = 400;
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
		
		// klikanie w tytuł
		$("#content .item .title").on("click", function() {
			if($(this).parent().find(".description:hidden").length == 1) {
				$(this).parent().find(".description").show(200);
				$(this).css("font-weight", "bold");
			} else {
				$(this).parent().find(".description").hide(100);
				$(this).css("font-weight", "normal");
			}
		});
	};
}());

$(document).on("ready", function() {
	new Main();
});

