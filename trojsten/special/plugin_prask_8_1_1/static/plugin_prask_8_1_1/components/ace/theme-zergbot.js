ace.define("ace/theme/zergbot",["require","exports","module","ace/lib/dom"], function(require, exports, module) {

	exports.isDark = true;
	exports.cssClass = "ace-zergbot";
	exports.cssText = ".ace-zergbot {\
background-color: #333333;\
color: #aaaaaa\
}\
.ace_gutter {\
background-color: #383838;\
color: #6a831e\
}\
.ace_cursor {\
color: #6a831e\
}\
.ace_selection {\
background: #6a831e\
}\
.ace_active-line {\
background-color: rgba(106, 131, 30, 0.1)\
}\
.ace_executing {\
background-color: #6a831e;\
position: relative\
}\
.ace_gutter-active-line {\
background-color: rgba(106, 131, 30, 0.15)\
}";

var dom = require("../lib/dom");
	dom.importCssString(exports.cssText, exports.cssClass);
});
