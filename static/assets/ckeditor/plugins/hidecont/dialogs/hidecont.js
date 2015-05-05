(function() {
	function nl2br(content){
		return content.replace(/\n/g, "<br />")
	}
    CKEDITOR.dialog.add("hidecont",
	    function(edt) {
	        // Size adjustments.
			var size = CKEDITOR.document.getWindow().getViewPaneSize(),
				// Make it maximum 800px wide, but still fully visible in the viewport.
				width = Math.min( size.width - 70, 800 ),
				// Make it use 2/3 of the viewport height.
				height = size.height / 1.5,

				clientHeight = document.documentElement.clientHeight ;

			// Low resolution settings.
			if ( clientHeight < 650 ) {
				height = clientHeight - 220;
			}
	        return {
	            title: "插入隐藏内容",
	            resizable: CKEDITOR.DIALOG_RESIZE_NONE,
	            minHeight: 200,
	            contents: [{
	                id: "hidecont",
	                elements: [
	                   {
							id: 'code',
							type: 'textarea',
							label: "插入隐藏内容，若插入隐藏内容，那么收费主题将只针对隐藏内容收费，其他部分公开。",
							setup: function( widget ) {
								this.setValue( widget.data.code );
							},
							commit: function( widget ) {
								widget.setData( 'code', this.getValue() );
							},
							inputStyle: 'cursor:auto;' +
								'width:' + width + 'px;' +
								'height:' + height + 'px;' +
								'tab-size:4;' +
								'text-align:left;resize:auto;margin-top:5px;',
							'class': 'cke_source'
						}
	                ]
	            }],

	            onOk: function() {
	                var content = this.getValueOf('hidecont', 'code');
	                content = CKEDITOR.tools.htmlEncode(content);
	                content = nl2br(content);
					edt.insertHtml("[hide]<br />"+content+"<br />[/hide]");
				}

	        }
	    })
})();