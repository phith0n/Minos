$(document).ready(function(){
	var storage_name = "savetext";
	var editor = new Simditor({
	  textarea: $('#editor'),
	  defaultImage: "/static/assets/simditor/images/image.png",
	  toolbar: [
		  'title',
		  'bold',
		  'italic',
		  'underline',
		  'strikethrough',
		  'color',
		  '|',
		  'ol',
		  'ul',
		  'blockquote',
		  'code',
		  'table',
		  '|',
		  'link',
		  'image',
		  'hr',
		  '|',
		  'indent',
		  'outdent',
		  '|',
		  'source',
		],
	  upload: {
	    url: "/uploader",
	    fileKey: "upload",
	    connectionCount: 1,
	    leaveConfirm: '正在上传文件，如果离开上传会自动取消'
	  }
	});
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
	if(window.localStorage){
		$("#save").click(function(){
			var text = editor.getValue();
			window.localStorage.setItem(storage_name, text);
		});
		var text = window.localStorage.getItem(storage_name);
		if(text){
			editor.setValue(text);
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