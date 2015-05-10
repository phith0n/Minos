$(document).ready(function(){
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

});