(function() {
    CKEDITOR.plugins.add("hidecont", {
        requires: "dialog,widget",
        init: function(a) {
            a.addCommand("hidecont", new CKEDITOR.dialogCommand("hidecont"));
            a.ui.addButton("Hidecont", {
                label: "插入隐藏内容",//调用dialog时显示的名称
                command: "hidecont",
                icon: this.path + "hidden.png"//在toolbar中的图标
            });

        },
        onLoad: function() {
            CKEDITOR.dialog.add( "hidecont", this.path + "dialogs/hidecont.js");
		}

    });

})();