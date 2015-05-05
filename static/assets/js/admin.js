$(document).on("ready", function(){
	function randomChar(l)  {
		var x="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
		var tmp="";
		var timestamp = new Date().getTime();
		for(var i=0 ; i < l ; i++)  {
			tmp += x.charAt( Math.ceil( Math.random() * 100000000 ) % x.length );
		}
		return tmp;
	}
	$("#create-key").on("click", function(){
		var key = randomChar(20);
		$("input[name='key']").val(key);
	})
	if(typeof ZeroClipboard != "undefined"){
		var client = new ZeroClipboard($(".zero-copy"));
		client.on( "ready", function( readyEvent ) {
			client.on( "copy", function (event) {
			  var i = event.target.name;
			  var clipboard = event.clipboardData;
			  clipboard.setData( "text/plain", $(".invite-" + i).text() );
			});
		})
	}

	$("#invite-act button.act").on("click", function(){
		var act = this.name;
		$("#invite-act input[name='action']").val(act);
		$("#invite-act").submit();
	})
})