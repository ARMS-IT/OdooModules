//===========================================
// Full Screen Mode
//===========================================

odoo.define('sh_backmate_theme_adv.full_screen_systray', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');    
    var SystrayMenu = require('web.SystrayMenu');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;

    var FullScreenTemplate = Widget.extend({
        template: "FullScreenTemplate",
        events: {
            'click .expand_img': '_click_expand_button',
			'click .compress_img': '_click_compress_button',
        },
        init: function () {
        	 this._super.apply(this, arguments);
             var self = this;
        },

        _click_expand_button: function (ev) {
        	ev.preventDefault();
            var self = this;
            $('.expand_img').css("display","none");
            $('.compress_img').css("display","block");
            var elem = document.querySelector('body');
			  if (elem.requestFullscreen) {
			    elem.requestFullscreen();
			  } else if (elem.mozRequestFullScreen) { /* Firefox */
			    elem.mozRequestFullScreen();
			  } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
			    elem.webkitRequestFullscreen();
			  } else if (elem.msRequestFullscreen) { /* IE/Edge */
			    elem.msRequestFullscreen();
			  }
        },
        _click_compress_button: function (ev) {
        	ev.preventDefault();
            var self = this;
            $('.compress_img').css("display","none");
            $('.expand_img').css("display","block");
            var elem = document.querySelector('body');
            if (document.exitFullscreen) {
				    document.exitFullscreen();
				  } else if (document.mozCancelFullScreen) { /* Firefox */
				    document.mozCancelFullScreen();
				  } else if (document.webkitExitFullscreen) { /* Chrome, Safari and Opera */
				    document.webkitExitFullscreen();
				  } else if (document.msExitFullscreen) { /* IE/Edge */
				    document.msExitFullscreen();
				  }
        },

    });

    FullScreenTemplate.prototype.sequence = 2;
    // session.user_has_group('sh_backmate_theme_adv.group_full_screen_mode').then(function(has_group) {
    // 	if(has_group){
    // 		 SystrayMenu.Items.push(FullScreenTemplate);
    // 	}
    // });
    rpc.query({
      model: 'res.users',
      method: 'search_read',
      fields: ['sh_enable_full_screen_mode'],
      domain: [['id', '=', session.uid]]
    }, { async: false }).then(function (data) {
      if (data) {
        _.each(data, function (user) {
          if (user.sh_enable_full_screen_mode) {
            SystrayMenu.Items.push(FullScreenTemplate);
  
          }
        });
  
      }
    });
   

   return {
	   FullScreenTemplate: FullScreenTemplate,
   };
});
//===========================================
// Night Mode
//===========================================

odoo.define('sh_backmate_theme_adv.night_mode_systray', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');    
    var SystrayMenu = require('web.SystrayMenu');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;
    
    var NightModeTemplate = Widget.extend({
        template: "NightModeTemplate",
        events: {
            'click #sun_button': '_click_sun_button',
			'click #moon_button': '_click_moon_button',
        },
        init: function () {
        	 this._super.apply(this, arguments);
             var self = this;
     		console.log("$('.o_web_client').hasClass('sh_night_mode')", $('.o_web_client'), $('.o_web_client').hasClass('sh_night_mode'))
			if ($('.o_web_client').hasClass('sh_night_mode')) {
				$('#moon_button').css("display", "none");
				$('#sun_button').css("display", "inline-flex");
			} else {
				$('#moon_button').css("display", "inline-flex");
				$('#sun_button').css("display", "none");
			}
        },

        _click_sun_button: function (ev) {
        	ev.preventDefault();
            var self = this;
			$('.o_web_client').removeClass('sh_night_mode');
			$('#moon_button').css("display", "inline-flex");
			$('#sun_button').css("display", "none");
        },
        _click_moon_button: function (ev) {
        	ev.preventDefault();
            var self = this;
 		   $('.o_web_client').addClass('sh_night_mode');
			$('#moon_button').css("display", "none");
			$('#sun_button').css("display", "inline-flex");
        },

    });

    NightModeTemplate.prototype.sequence = 99;

	rpc.query({
		model: 'res.users',
		method: 'search_read',
		fields: ['sh_enable_night_mode'],
		domain: [['id', '=', session.uid]]
	}, { async: false }).then(function (data) {
		if (data) {
			_.each(data, function (user) {
				if (user.sh_enable_night_mode) {
					SystrayMenu.Items.push(NightModeTemplate);

				}
			});

		}
	});


    // session.user_has_group('sh_backmate_theme_adv.group_night_mode').then(function(has_group) {
    // 	if(has_group){
    // 		SystrayMenu.Items.push(NightModeTemplate);
    // 	}
    // });
    
   return {
	   NightModeTemplate: NightModeTemplate,
   };
});


//odoo.define('sh_backmate_theme_adv.night_mode', function(require) 
//{
//
//	var ajax = require('web.ajax');
// 	var rpc = require('web.rpc');
// 	$(document).ready(function() 
//	{		

// 		var toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
// 		var currentTheme = localStorage.getItem('theme');
// 		if (currentTheme) {
// 		    document.documentElement.setAttribute('data-theme', currentTheme);
// 		}
// 		
// 		$(document).on('click','#night_checkbox',function(e){
// 			if (e.target.checked) {
// 		        document.documentElement.setAttribute('data-theme', 'dark');
// 		       localStorage.setItem('theme', 'dark');
//
//		    	rpc.query({
//	                model: 'sh.back.theme.config.settings',
//	                method: 'activate_primary_variable_scss',
//	               args: [[]],
//	            } ,{async: false}).then(function(output) {
//	            });
//		    	 location.reload(true);
// 		    }
// 		    else {
//
// 		    	 rpc.query({
// 	                model: 'sh.back.theme.config.settings',
// 	                method: 'deactivate_primary_variable_scss',
// 	               args: [[]],
// 	            } ,{async: false}).then(function(output) {
// 	            });
// 		    	document.documentElement.setAttribute('data-theme', 'light');
// 		         localStorage.setItem('theme', 'light');
// 		        location.reload(true);
//
// 		        
// 		          
// 		    }   
// 		});
 		
// 		$(document).on('click','.open_full_screen',function(e){
// 			var elem = document.querySelector('body');
// 			if ($('#fullscreen_checkbox').prop("checked") == false) {
// 				$('#fullscreen_checkbox').attr('checked', true)
// 				$('.compress_img').css("display","block");
// 				$('.expand_img').css("display","none");
//				  if (elem.requestFullscreen) {
//				    elem.requestFullscreen();
//				  } else if (elem.mozRequestFullScreen) { /* Firefox */
//				    elem.mozRequestFullScreen();
//				  } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
//				    elem.webkitRequestFullscreen();
//				  } else if (elem.msRequestFullscreen) { /* IE/Edge */
//				    elem.msRequestFullscreen();
//				  }
// 			}else{
// 				
// 				$('#fullscreen_checkbox').attr('checked', false)
// 				$('.compress_img').css("display","none");
// 				$('.expand_img').css("display","block");
// 				if (document.exitFullscreen) {
// 				    document.exitFullscreen();
// 				  } else if (document.mozCancelFullScreen) { /* Firefox */
// 				    document.mozCancelFullScreen();
// 				  } else if (document.webkitExitFullscreen) { /* Chrome, Safari and Opera */
// 				    document.webkitExitFullscreen();
// 				  } else if (document.msExitFullscreen) { /* IE/Edge */
// 				    document.msExitFullscreen();
// 				  }
// 				
// 			}	
// 		});
// 		
// 		function switchTheme(e) {
// 			alert()
// 		     
// 		}

 		
// 		
//			
//	}); 	
//    
//});
