(function($) {
  'use strict';

  jQuery.cookie = function(name, value, options) {
	if (typeof value != 'undefined') {
	   options = options || {};
	   if (value === null) {
		value = '';
		options = $.extend({}, options);
		options.expires = -1;
	   }
	   var expires = '';
	   if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
		var date;
		if (typeof options.expires == 'number') {
		 date = new Date();
		 date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
		} else {
		 date = options.expires;
		}
		expires = '; expires=' + date.toUTCString();
	   }
	   var path = options.path ? '; path=' + (options.path) : '';
	   var domain = options.domain ? '; domain=' + (options.domain) : '';
	   var secure = options.secure ? '; secure' : '';
	   document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
	} else {
	   var cookieValue = null;
	   if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
		 var cookie = jQuery.trim(cookies[i]);
		 if (cookie.substring(0, name.length + 1) == (name + '=')) {
		  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		  break;
		 }
		}
	   }
	   return cookieValue;
	}
  };

  $(function() {
    $('#doc-my-tabs').tabs({noSwipe: 1});
    $("[href='#back']").click(function(){
        history.back(-1);
        return false;
    })

    var $fullText = $('.admin-fullText');
    $('#admin-fullscreen').on('click', function() {
      $.AMUI.fullscreen.toggle();
    });

    $(document).on($.AMUI.fullscreen.raw.fullscreenchange, function() {
      $.AMUI.fullscreen.isFullscreen ? $fullText.text('关闭全屏') : $fullText.text('开启全屏');
    });

	if($("#login-name").val()){
		$.ajax({
	        "url": "/ajax/newmsg",
	        "type": "post",
	        "dataType": "json",
	        "data": {
	            "_xsrf": $.cookie("_xsrf")
	        },
	        "success": function(data){
	            var count = parseInt(data["info"]);
	            if(count > 0){
	                $("#newmsg").text(count);
	            }
	        }
	    })
	}
  });
})(jQuery);