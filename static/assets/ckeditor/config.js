/**
 * @license Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	//config.height = '25em';
	// Flash
	config.skin = 'flat';
	config.toolbar =
    [
	    ['Source','-','NewPage','Preview','-','Templates'],
	    ['Undo', 'Redo', '-', 'SelectAll', 'RemoveFormat'],
	    ['Styles','Format','Font','FontSize'],
	    ['TextColor','BGColor'],
	    ['Maximize', 'ShowBlocks','-','About'],
	    '/',
	    ['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
	    ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
	    ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
	    ['Link','Unlink','Anchor'],
	    ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak'],
	    ['Code', 'CodeSnippet', 'Hidecont']
    ];
    config.extraPlugins = 'codesnippet,autogrow,hidecont';
	config.filebrowserImageUploadUrl = '/uploader';
	config.tabSpaces = 4;
	config.baseHref = '/';
};
