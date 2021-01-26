/*! geonode-assets 13-08-2019 */
 
define(["module"],function(a){"use strict";var b,c,d=["Msxml2.XMLHTTP","Microsoft.XMLHTTP","Msxml2.XMLHTTP.4.0"],e=/^\s*<\?xml(\s)+version=[\'\"](\d)*.(\d)*[\'\"](\s)*\?>/im,f=/<body[^>]*>\s*([\s\S]+)\s*<\/body>/im,g="undefined"!=typeof location&&location.href,h=g&&location.protocol&&location.protocol.replace(/\:/,""),i=g&&location.hostname,j=g&&(location.port||void 0),k=[],l=a.config&&a.config()||{};return b={version:"2.0.3",strip:function(a){if(a){a=a.replace(e,"");var b=a.match(f);b&&(a=b[1])}else a="";return a},jsEscape:function(a){return a.replace(/(['\\])/g,"\\$1").replace(/[\f]/g,"\\f").replace(/[\b]/g,"\\b").replace(/[\n]/g,"\\n").replace(/[\t]/g,"\\t").replace(/[\r]/g,"\\r").replace(/[\u2028]/g,"\\u2028").replace(/[\u2029]/g,"\\u2029")},createXhr:l.createXhr||function(){var a,b,c;if("undefined"!=typeof XMLHttpRequest)return new XMLHttpRequest;if("undefined"!=typeof ActiveXObject)for(b=0;b<3;b+=1){c=d[b];try{a=new ActiveXObject(c)}catch(a){}if(a){d=[c];break}}return a},parseName:function(a){var b=!1,c=a.indexOf("."),d=a.substring(0,c),e=a.substring(c+1,a.length);return c=e.indexOf("!"),-1!==c&&(b=e.substring(c+1,e.length),b="strip"===b,e=e.substring(0,c)),{moduleName:d,ext:e,strip:b}},xdRegExp:/^((\w+)\:)?\/\/([^\/\\]+)/,useXhr:function(a,c,d,e){var f,g,h,i=b.xdRegExp.exec(a);return!i||(f=i[2],g=i[3],g=g.split(":"),h=g[1],g=g[0],!(f&&f!==c||g&&g.toLowerCase()!==d.toLowerCase()||(h||g)&&h!==e))},finishLoad:function(a,c,d,e){d=c?b.strip(d):d,l.isBuild&&(k[a]=d),e(d)},load:function(a,c,d,e){if(e.isBuild&&!e.inlineText)return void d();l.isBuild=e.isBuild;var f=b.parseName(a),k=f.moduleName+"."+f.ext,m=c.toUrl(k),n=l.useXhr||b.useXhr;!g||n(m,h,i,j)?b.get(m,function(c){b.finishLoad(a,f.strip,c,d)},function(a){d.error&&d.error(a)}):c([k],function(a){b.finishLoad(f.moduleName+"."+f.ext,f.strip,a,d)})},write:function(a,c,d,e){if(k.hasOwnProperty(c)){var f=b.jsEscape(k[c]);d.asModule(a+"!"+c,"define(function () { return '"+f+"';});\n")}},writeFile:function(a,c,d,e,f){var g=b.parseName(c),h=g.moduleName+"."+g.ext,i=d.toUrl(g.moduleName+"."+g.ext)+".js";b.load(h,d,function(c){var d=function(a){return e(i,a)};d.asModule=function(a,b){return e.asModule(a,i,b)},b.write(a,h,d,f)},f)}},"node"===l.env||!l.env&&"undefined"!=typeof process&&process.versions&&process.versions.node?(c=require.nodeRequire("fs"),b.get=function(a,b){var d=c.readFileSync(a,"utf8");0===d.indexOf("\ufeff")&&(d=d.substring(1)),b(d)}):"xhr"===l.env||!l.env&&b.createXhr()?b.get=function(a,c,d){var e=b.createXhr();e.open("GET",a,!0),l.onXhr&&l.onXhr(e,a),e.onreadystatechange=function(b){var f,g;4===e.readyState&&(f=e.status,f>399&&f<600?(g=new Error(a+" HTTP status: "+f),g.xhr=e,d(g)):c(e.responseText))},e.send(null)}:("rhino"===l.env||!l.env&&"undefined"!=typeof Packages&&"undefined"!=typeof java)&&(b.get=function(a,b){var c,d,e=new java.io.File(a),f=java.lang.System.getProperty("line.separator"),g=new java.io.BufferedReader(new java.io.InputStreamReader(new java.io.FileInputStream(e),"utf-8")),h="";try{for(c=new java.lang.StringBuffer,d=g.readLine(),d&&d.length()&&65279===d.charAt(0)&&(d=d.substring(1)),c.append(d);null!==(d=g.readLine());)c.append(f),c.append(d);h=String(c.toString())}finally{g.close()}b(h)}),b});