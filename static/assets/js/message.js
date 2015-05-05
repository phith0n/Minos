$(document).ready(function(){
	$("#readall a").on("click", function(){
		$("#readall").submit();
		return false;
	});
	$("#deleteall a").on("click", function(){
		if(confirm("是否删除所有消息，该操作将不能恢复")){
			$("#deleteall").submit();
		}
		return false;
	});
})