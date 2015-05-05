$(document).on("ready", function(){
	$(".cancel-like").click(function(t){
		if(!confirm("是否取消赞这篇文章？")) return false;
		this.parentNode.submit();
		return false;
	})
	$(".cancel-bookmark").click(function(t){
		if(!confirm("是否取消收藏这篇文章？")) return false;
		this.parentNode.submit();
		return false;
	})
})