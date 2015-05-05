$("document").ready(function(){
	var captcha = document.getElementById("captcha");
	if(captcha) captcha.style.cursor = "pointer";
	$("#captcha").on("click", function(){
		this.src = "/captcha.png?" + Math.random();
	});

	invalid_msg = {
		"username": ""
	}
	$('#register-box').validator({
	       validate: function(validity){
				if(validity.field.name == "username")
				{
					return $.ajax({
						"url": "/nologin/checkusername",
						"type": "post",
						"dataType": "json",
						"data": {
							"_xsrf": $.AMUI.utils.cookie.get("_xsrf"),
							"username": validity.field.value
						}
					}).then(function(data){
						if(data["status"] == "success"){
							validity.valid = true;
						}else{
							validity.valid = false;
							invalid_msg[validity.field.name] = data["info"];
						}
						return validity;
					});
				}
	       },
	       onInValid: function(validity){
	        var $field = $(validity.field);
			var $group = $field.closest('.am-form-group .alert');
			var $alert = $group.find('.am-alert');
	        var msg = invalid_msg[validity.field.name] || ($field.data("error-msg") || this.getValidationMessage(validity));
	        if (!$alert.length) {
			   $alert = $('<div class="am-alert am-alert-danger"></div>').hide().
			   appendTo($group);
			}
			$alert.html(msg).show();
	       },
	       onValid: function(validity) {
		      $(validity.field).closest('.am-form-group .alert').find('.am-alert').hide();
		    },
	  });
})