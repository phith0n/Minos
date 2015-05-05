$(document).ready(function(){
	var storage_name = "savetext";
	$("#publish").click(function(){
		var title = $("[name='title']").val();
		if(!title){
			$("#title-form").addClass("am-form-error").addClass("am-form-feedback");
			$("[name='title']").attr("placeholder", "标题不能为空");
			return ;
		}
		if(window.localStorage){
			window.localStorage.clear(storage_name);
		}
		$("#minos-pulish").submit();
	});
	CKEDITOR.on("instanceReady", function(){
		if(window.localStorage){
			$("#save").click(function(){
				var text = CKEDITOR.instances.ckeditor.getData();
				window.localStorage.setItem(storage_name, text);
			});
			var text = window.localStorage.getItem(storage_name);
			if(text){
				CKEDITOR.instances.ckeditor.setData(text);
			}
			setInterval(function(){
				$("#save").click();
			}, 10000);
		}else{
			$("#save").click(function(){
				alert("你的浏览器不支持临时存储");
			});
		}
	})

})