$(document).ready(function(){
	//hljs.initHighlightingOnLoad();
	$("pre").each(function(i, block){
		var lang = $(this).attr("data-lang");
		if(lang)
		{
			$(this).attr("class", lang);
			hljs.configure({languages: lang});
			hljs.highlightBlock(block);
		}
	});
	$("#like").on("click", function(){
	    $.ajax({
	        "url": "/ajax/like",
	        "type": "post",
	        "data": {
	            "_xsrf": $.cookie("_xsrf"),
	            "post": $("#postid").val()
	        },
	        "dataType": "json",
	        "success": function(data){
                if(data["status"] == "success"){
                    $("#like .minos-act").text("顶(" + data["info"] + ")");
                }else if(data["info"] == "already unliked"){
                    alert("已经踩过啦，不允许再顶");
                }else if(data["info"] == "already liked"){
                    alert("已经顶过啦，拒绝刷票");
                }else{
                    alert("参数错误，请重试");
                }
	        }
	    })
	    return false;
	})
	$("#unlike").on("click", function(){
	    $.ajax({
	        "url": "/ajax/unlike",
	        "type": "post",
	        "data": {
	            "_xsrf": $.cookie("_xsrf"),
	            "post": $("#postid").val()
	        },
	        "dataType": "json",
	        "success": function(data){
                if(data["status"] == "success"){
                    $("#unlike .minos-act").text("踩(" + data["info"] + ")");
                }else if(data["info"] == "already unliked"){
                    alert("已经踩过啦，别这么狠呀");
                }else if(data["info"] == "already liked"){
                    alert("已经顶过啦，不允许再踩");
                }else{
                    alert("参数错误，请重试");
                }
	        }
	    })
	    return false;
	});
	$("#bookmark").on("click", function(){
		$.ajax({
			"url": "/ajax/bookmark",
			"type": "post",
			"dataType": "json",
			"data": {
				"_xsrf": $.cookie("_xsrf"),
				"post": $("#postid").val()
			},
			"success": function(data){
				if(data["status"] == "success"){
					alert("收藏成功")
				}else if(data["info"] == "already bookmark"){
					alert("已经收藏过啦");
				}else{
					alert("参数错误，请重试");
				}
			}
		})
		return false;
	});
	$("article img").each(function(){
		this.style.height = "auto";
	})
	$("#star a").on("click", function(){
		if (this.hash == "#star") {
			$("#star [name='method']").val('unstar');
			$("#star").submit();
		}else if(this.hash == "#unstar") {
			$("#star [name='method']").val('star');
			$("#star").submit();
		}
		return false;
	})
	$("#delete a").on("click", function(){
		if(confirm("是否删除这篇文章，删除将不能恢复")){
			$("#delete [name='method']").val('del');
			$("#delete").submit();
		}
		return false;
	});
	$("#open a").on("click", function(){
		if (this.hash == "#open") {
			$("#open [name='method']").val('close');
			$("#open").submit();
		}else if(this.hash == "#close") {
			$("#open [name='method']").val('open');
			$("#open").submit();
		}
		return false;
	})
	$("#top a").on("click", function(){
		if (this.hash == "#top") {
			$("#open [name='method']").val('notop');
			$("#open").submit();
		}else if(this.hash == "#notop") {
			$("#open [name='method']").val('top');
			$("#open").submit();
		}
		return false;
	})
	$("#rank a").on("click", function(){
		var rank = prompt("输入奖励或惩罚的分数");
		if (!rank || parseInt(rank) == 0){
			return false;
		}
		$("#rank [name='method']").val('rank');
		$("#rank [name='rank']").val(rank);
		$("#rank").submit();
		return false;
	});
	$(".hidecont form").on("submit", function(){
		if(!confirm("是否确定购买这篇帖子")){
			return false;
		}
	});
	$("#thanks").on("click", function(){
		if(!confirm("感谢将会支付1金币给文章发表者，是否确认")){
			return false;
		}
		lang = {
			"post not exists!": "文章不存在",
			"already thanks": "你已经感谢过啦",
			"cannot thanks to yourself": "不能感谢自己",
			"money not enough": "你没钱感谢了",
		}
		$.ajax({
			"url": "/ajax/thanks",
			"type": "post",
			"dataType": "json",
			"data": {
				"_xsrf": $.cookie("_xsrf"),
				"id": $("#postid").val()
			},
			"success": function(data){
				if(data["status"] == "fail"){
					alert(lang[data["info"]]);
				}else{
					alert("感谢成功");
				}
			}
		})
		return false;
	});
	$("a[href='del-comment']").on("click", function(){
		if(!confirm("是否删除这条评论")){
			return false;
		}
		this.parentNode.submit();
		return false;
	});
	$("a[href='reply-comment']").on("click", function(){
		var comm = $("#comment").val();
		var username = this.name;
		comm = username + " " + comm;
		$("#comment").val(comm).focus();
		return false;
	})
	$(".minos-at").each(function(){
		var txt = $(this).text();
		//666666
		txt = txt.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;").replace(/>/g, "&gt;")
			.replace(/'/g, "&#039;").replace(/"/g, "&quot;");
		txt = txt.replace(/@([a-zA-Z0-9_\-\u4e00-\u9fa5]+)/g, '<a href="/user/detail/$1">@$1</a>');
		txt = txt.replace(/\n/g, "<br />");
		$(this).html(txt);
	});
	(function(){
		var captcha = document.getElementById("captcha");
		if(captcha) captcha.style.cursor = "pointer";
		$("#captcha").on("click", function(){
			this.src = "/captcha.png?" + Math.random();
		});
		$(".bdsharebuttonbox a.am-icon-weixin").click(function(){
			var script = document.createElement("script");
			script.setAttribute("type","text/javascript");
			script.onload = function() {
				$("#qrcode").html("");
				new QRCode("qrcode", {
				    text: location.href,
				    width: 128,
				    height: 128,
				    colorDark : "#000000",
				    colorLight : "#ffffff",
				    correctLevel : QRCode.CorrectLevel.H
				});
				$("#show-qrcode").modal({
					width: 150
				});
			}
			script.setAttribute("src", '/static/assets/js/qrcode.min.js?cdnversion='+~(-new Date()/36e5));
			(document.getElementsByTagName('head')[0]||body).appendChild(script);
			return false;
		})

		// 百度分享
		window._bd_share_config={
			"common":{
				"bdSnsKey":{},
				"bdText":"分享一篇来自Minos的文章",
				"bdMini":"2",
				"bdMiniList":false,
				"bdPic":"",
				"bdStyle":"0",
				"bdSize":"16",
				"bdSign": "off",
			},
			"share":{
				"bdCustomStyle": "/static/assets/css/none.css"
			}
		};
		with(document)0[
			(getElementsByTagName('head')[0]||body)
				.appendChild(createElement('script'))
				.src='http://bdimg.share.baidu.com/static/api/js/share.js?v=89860593.js?cdnversion='+~(-new Date()/36e5)
		];

		// 百度分享
	})();
});