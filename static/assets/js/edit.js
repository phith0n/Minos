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

	});

});