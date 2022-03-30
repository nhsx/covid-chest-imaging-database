(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[234],{7645:function(e,t,n){"use strict";function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{},i=Object.keys(n);"function"===typeof Object.getOwnPropertySymbols&&(i=i.concat(Object.getOwnPropertySymbols(n).filter((function(e){return Object.getOwnPropertyDescriptor(n,e).enumerable})))),i.forEach((function(t){r(e,t,n[t])}))}return e}t.default=function(e,t){var n=s.default,r={loading:function(e){e.error,e.isLoading;return e.pastDelay,null}};a=e,u=Promise,(null!=u&&"undefined"!==typeof Symbol&&u[Symbol.hasInstance]?u[Symbol.hasInstance](a):a instanceof u)?r.loader=function(){return e}:"function"===typeof e?r.loader=e:"object"===typeof e&&(r=i({},r,e));var a,u;var l=r=i({},r,t);if(l.suspense)throw new Error("Invalid suspense option usage in next/dynamic. Read more: https://nextjs.org/docs/messages/invalid-dynamic-suspense");if(l.suspense)return n(l);r.loadableGenerated&&delete(r=i({},r,r.loadableGenerated)).loadableGenerated;if("boolean"===typeof r.ssr){if(!r.ssr)return delete r.ssr,o(n,r);delete r.ssr}return n(r)};a(n(7294));var s=a(n(4588));function a(e){return e&&e.__esModule?e:{default:e}}function o(e,t){return delete t.webpack,delete t.modules,e(t)}},3644:function(e,t,n){"use strict";var r;Object.defineProperty(t,"__esModule",{value:!0}),t.LoadableContext=void 0;var i=((r=n(7294))&&r.__esModule?r:{default:r}).default.createContext(null);t.LoadableContext=i},4588:function(e,t,n){"use strict";function r(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}function i(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function s(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{},r=Object.keys(n);"function"===typeof Object.getOwnPropertySymbols&&(r=r.concat(Object.getOwnPropertySymbols(n).filter((function(e){return Object.getOwnPropertyDescriptor(n,e).enumerable})))),r.forEach((function(t){i(e,t,n[t])}))}return e}Object.defineProperty(t,"__esModule",{value:!0}),t.default=void 0;var a,o=(a=n(7294))&&a.__esModule?a:{default:a},u=n(7161),l=n(3644);var c=[],f=[],d=!1;function h(e){var t=e(),n={loading:!0,loaded:null,error:null};return n.promise=t.then((function(e){return n.loading=!1,n.loaded=e,e})).catch((function(e){throw n.loading=!1,n.error=e,e})),n}var p=function(){function e(t,n){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this._loadFn=t,this._opts=n,this._callbacks=new Set,this._delay=null,this._timeout=null,this.retry()}var t,n,i;return t=e,(n=[{key:"promise",value:function(){return this._res.promise}},{key:"retry",value:function(){var e=this;this._clearTimeouts(),this._res=this._loadFn(this._opts.loader),this._state={pastDelay:!1,timedOut:!1};var t=this._res,n=this._opts;if(t.loading){if("number"===typeof n.delay)if(0===n.delay)this._state.pastDelay=!0;else{var r=this;this._delay=setTimeout((function(){r._update({pastDelay:!0})}),n.delay)}if("number"===typeof n.timeout){var i=this;this._timeout=setTimeout((function(){i._update({timedOut:!0})}),n.timeout)}}this._res.promise.then((function(){e._update({}),e._clearTimeouts()})).catch((function(t){e._update({}),e._clearTimeouts()})),this._update({})}},{key:"_update",value:function(e){this._state=s({},this._state,{error:this._res.error,loaded:this._res.loaded,loading:this._res.loading},e),this._callbacks.forEach((function(e){return e()}))}},{key:"_clearTimeouts",value:function(){clearTimeout(this._delay),clearTimeout(this._timeout)}},{key:"getCurrentValue",value:function(){return this._state}},{key:"subscribe",value:function(e){var t=this;return this._callbacks.add(e),function(){t._callbacks.delete(e)}}}])&&r(t.prototype,n),i&&r(t,i),e}();function m(e){return function(e,t){var n=function(){if(!i){var t=new p(e,r);i={getCurrentValue:t.getCurrentValue.bind(t),subscribe:t.subscribe.bind(t),retry:t.retry.bind(t),promise:t.promise.bind(t)}}return i.promise()},r=Object.assign({loader:null,loading:null,delay:200,timeout:null,webpack:null,modules:null,suspense:!1},t);r.suspense&&(r.lazy=o.default.lazy(r.loader));var i=null;if(!d&&!r.suspense){var a=r.webpack?r.webpack():r.modules;a&&f.push((function(e){var t=!0,r=!1,i=void 0;try{for(var s,o=a[Symbol.iterator]();!(t=(s=o.next()).done);t=!0){var u=s.value;if(-1!==e.indexOf(u))return n()}}catch(l){r=!0,i=l}finally{try{t||null==o.return||o.return()}finally{if(r)throw i}}}))}var c=r.suspense?function(e,t){return o.default.createElement(r.lazy,s({},e,{ref:t}))}:function(e,t){n();var s=o.default.useContext(l.LoadableContext),a=u.useSubscription(i);return o.default.useImperativeHandle(t,(function(){return{retry:i.retry}}),[]),s&&Array.isArray(r.modules)&&r.modules.forEach((function(e){s(e)})),o.default.useMemo((function(){return a.loading||a.error?o.default.createElement(r.loading,{isLoading:a.loading,pastDelay:a.pastDelay,timedOut:a.timedOut,error:a.error,retry:i.retry}):a.loaded?o.default.createElement(function(e){return e&&e.__esModule?e.default:e}(a.loaded),e):null}),[e,a])};return c.preload=function(){return!r.suspense&&n()},c.displayName="LoadableComponent",o.default.forwardRef(c)}(h,e)}function g(e,t){for(var n=[];e.length;){var r=e.pop();n.push(r(t))}return Promise.all(n).then((function(){if(e.length)return g(e,t)}))}m.preloadAll=function(){return new Promise((function(e,t){g(c).then(e,t)}))},m.preloadReady=function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:[];return new Promise((function(t){var n=function(){return d=!0,t()};g(f,e).then(n,n)}))},window.__NEXT_PRELOADREADY=m.preloadReady;var _=m;t.default=_},5152:function(e,t,n){e.exports=n(7645)},7460:function(e,t){var n,r,i;r=[],n=function e(){"use strict";var t="undefined"!=typeof self?self:"undefined"!=typeof window?window:void 0!==t?t:{},n=!t.document&&!!t.postMessage,r=n&&/blob:/i.test((t.location||{}).protocol),i={},s=0,a={parse:function(n,r){var o=(r=r||{}).dynamicTyping||!1;if(w(o)&&(r.dynamicTypingFunction=o,o={}),r.dynamicTyping=o,r.transform=!!w(r.transform)&&r.transform,r.worker&&a.WORKERS_SUPPORTED){var u=function(){if(!a.WORKERS_SUPPORTED)return!1;var n,r,o=(n=t.URL||t.webkitURL||null,r=e.toString(),a.BLOB_URL||(a.BLOB_URL=n.createObjectURL(new Blob(["(",r,")();"],{type:"text/javascript"})))),u=new t.Worker(o);return u.onmessage=g,u.id=s++,i[u.id]=u}();return u.userStep=r.step,u.userChunk=r.chunk,u.userComplete=r.complete,u.userError=r.error,r.step=w(r.step),r.chunk=w(r.chunk),r.complete=w(r.complete),r.error=w(r.error),delete r.worker,void u.postMessage({input:n,config:r,workerId:u.id})}var h=null;return a.NODE_STREAM_INPUT,"string"==typeof n?h=r.download?new l(r):new f(r):!0===n.readable&&w(n.read)&&w(n.on)?h=new d(r):(t.File&&n instanceof File||n instanceof Object)&&(h=new c(r)),h.stream(n)},unparse:function(e,t){var n=!1,r=!0,i=",",s="\r\n",o='"',u=o+o,l=!1,c=null,f=!1;!function(){if("object"==typeof t){if("string"!=typeof t.delimiter||a.BAD_DELIMITERS.filter((function(e){return-1!==t.delimiter.indexOf(e)})).length||(i=t.delimiter),("boolean"==typeof t.quotes||"function"==typeof t.quotes||Array.isArray(t.quotes))&&(n=t.quotes),"boolean"!=typeof t.skipEmptyLines&&"string"!=typeof t.skipEmptyLines||(l=t.skipEmptyLines),"string"==typeof t.newline&&(s=t.newline),"string"==typeof t.quoteChar&&(o=t.quoteChar),"boolean"==typeof t.header&&(r=t.header),Array.isArray(t.columns)){if(0===t.columns.length)throw new Error("Option columns is empty");c=t.columns}void 0!==t.escapeChar&&(u=t.escapeChar+o),("boolean"==typeof t.escapeFormulae||t.escapeFormulae instanceof RegExp)&&(f=t.escapeFormulae instanceof RegExp?t.escapeFormulae:/^[=+\-@\t\r].*$/)}}();var d=new RegExp(p(o),"g");if("string"==typeof e&&(e=JSON.parse(e)),Array.isArray(e)){if(!e.length||Array.isArray(e[0]))return h(null,e,l);if("object"==typeof e[0])return h(c||Object.keys(e[0]),e,l)}else if("object"==typeof e)return"string"==typeof e.data&&(e.data=JSON.parse(e.data)),Array.isArray(e.data)&&(e.fields||(e.fields=e.meta&&e.meta.fields||c),e.fields||(e.fields=Array.isArray(e.data[0])?e.fields:"object"==typeof e.data[0]?Object.keys(e.data[0]):[]),Array.isArray(e.data[0])||"object"==typeof e.data[0]||(e.data=[e.data])),h(e.fields||[],e.data||[],l);throw new Error("Unable to serialize unrecognized input");function h(e,t,n){var a="";"string"==typeof e&&(e=JSON.parse(e)),"string"==typeof t&&(t=JSON.parse(t));var o=Array.isArray(e)&&0<e.length,u=!Array.isArray(t[0]);if(o&&r){for(var l=0;l<e.length;l++)0<l&&(a+=i),a+=m(e[l],l);0<t.length&&(a+=s)}for(var c=0;c<t.length;c++){var f=o?e.length:t[c].length,d=!1,h=o?0===Object.keys(t[c]).length:0===t[c].length;if(n&&!o&&(d="greedy"===n?""===t[c].join("").trim():1===t[c].length&&0===t[c][0].length),"greedy"===n&&o){for(var p=[],g=0;g<f;g++){var _=u?e[g]:g;p.push(t[c][_])}d=""===p.join("").trim()}if(!d){for(var y=0;y<f;y++){0<y&&!h&&(a+=i);var v=o&&u?e[y]:y;a+=m(t[c][v],y)}c<t.length-1&&(!n||0<f&&!h)&&(a+=s)}}return a}function m(e,t){if(null==e)return"";if(e.constructor===Date)return JSON.stringify(e).slice(1,25);var r=!1;f&&"string"==typeof e&&f.test(e)&&(e="'"+e,r=!0);var s=e.toString().replace(d,u);return(r=r||!0===n||"function"==typeof n&&n(e,t)||Array.isArray(n)&&n[t]||function(e,t){for(var n=0;n<t.length;n++)if(-1<e.indexOf(t[n]))return!0;return!1}(s,a.BAD_DELIMITERS)||-1<s.indexOf(i)||" "===s.charAt(0)||" "===s.charAt(s.length-1))?o+s+o:s}}};if(a.RECORD_SEP=String.fromCharCode(30),a.UNIT_SEP=String.fromCharCode(31),a.BYTE_ORDER_MARK="\ufeff",a.BAD_DELIMITERS=["\r","\n",'"',a.BYTE_ORDER_MARK],a.WORKERS_SUPPORTED=!n&&!!t.Worker,a.NODE_STREAM_INPUT=1,a.LocalChunkSize=10485760,a.RemoteChunkSize=5242880,a.DefaultDelimiter=",",a.Parser=m,a.ParserHandle=h,a.NetworkStreamer=l,a.FileStreamer=c,a.StringStreamer=f,a.ReadableStreamStreamer=d,t.jQuery){var o=t.jQuery;o.fn.parse=function(e){var n=e.config||{},r=[];return this.each((function(e){if("INPUT"!==o(this).prop("tagName").toUpperCase()||"file"!==o(this).attr("type").toLowerCase()||!t.FileReader||!this.files||0===this.files.length)return!0;for(var i=0;i<this.files.length;i++)r.push({file:this.files[i],inputElem:this,instanceConfig:o.extend({},n)})})),i(),this;function i(){if(0!==r.length){var t,n,i,u,l=r[0];if(w(e.before)){var c=e.before(l.file,l.inputElem);if("object"==typeof c){if("abort"===c.action)return t="AbortError",n=l.file,i=l.inputElem,u=c.reason,void(w(e.error)&&e.error({name:t},n,i,u));if("skip"===c.action)return void s();"object"==typeof c.config&&(l.instanceConfig=o.extend(l.instanceConfig,c.config))}else if("skip"===c)return void s()}var f=l.instanceConfig.complete;l.instanceConfig.complete=function(e){w(f)&&f(e,l.file,l.inputElem),s()},a.parse(l.file,l.instanceConfig)}else w(e.complete)&&e.complete()}function s(){r.splice(0,1),i()}}}function u(e){this._handle=null,this._finished=!1,this._completed=!1,this._halted=!1,this._input=null,this._baseIndex=0,this._partialLine="",this._rowCount=0,this._start=0,this._nextChunk=null,this.isFirstChunk=!0,this._completeResults={data:[],errors:[],meta:{}},function(e){var t=v(e);t.chunkSize=parseInt(t.chunkSize),e.step||e.chunk||(t.chunkSize=null),this._handle=new h(t),(this._handle.streamer=this)._config=t}.call(this,e),this.parseChunk=function(e,n){if(this.isFirstChunk&&w(this._config.beforeFirstChunk)){var i=this._config.beforeFirstChunk(e);void 0!==i&&(e=i)}this.isFirstChunk=!1,this._halted=!1;var s=this._partialLine+e;this._partialLine="";var o=this._handle.parse(s,this._baseIndex,!this._finished);if(!this._handle.paused()&&!this._handle.aborted()){var u=o.meta.cursor;this._finished||(this._partialLine=s.substring(u-this._baseIndex),this._baseIndex=u),o&&o.data&&(this._rowCount+=o.data.length);var l=this._finished||this._config.preview&&this._rowCount>=this._config.preview;if(r)t.postMessage({results:o,workerId:a.WORKER_ID,finished:l});else if(w(this._config.chunk)&&!n){if(this._config.chunk(o,this._handle),this._handle.paused()||this._handle.aborted())return void(this._halted=!0);o=void 0,this._completeResults=void 0}return this._config.step||this._config.chunk||(this._completeResults.data=this._completeResults.data.concat(o.data),this._completeResults.errors=this._completeResults.errors.concat(o.errors),this._completeResults.meta=o.meta),this._completed||!l||!w(this._config.complete)||o&&o.meta.aborted||(this._config.complete(this._completeResults,this._input),this._completed=!0),l||o&&o.meta.paused||this._nextChunk(),o}this._halted=!0},this._sendError=function(e){w(this._config.error)?this._config.error(e):r&&this._config.error&&t.postMessage({workerId:a.WORKER_ID,error:e,finished:!1})}}function l(e){var t;(e=e||{}).chunkSize||(e.chunkSize=a.RemoteChunkSize),u.call(this,e),this._nextChunk=n?function(){this._readChunk(),this._chunkLoaded()}:function(){this._readChunk()},this.stream=function(e){this._input=e,this._nextChunk()},this._readChunk=function(){if(this._finished)this._chunkLoaded();else{if(t=new XMLHttpRequest,this._config.withCredentials&&(t.withCredentials=this._config.withCredentials),n||(t.onload=b(this._chunkLoaded,this),t.onerror=b(this._chunkError,this)),t.open(this._config.downloadRequestBody?"POST":"GET",this._input,!n),this._config.downloadRequestHeaders){var e=this._config.downloadRequestHeaders;for(var r in e)t.setRequestHeader(r,e[r])}if(this._config.chunkSize){var i=this._start+this._config.chunkSize-1;t.setRequestHeader("Range","bytes="+this._start+"-"+i)}try{t.send(this._config.downloadRequestBody)}catch(e){this._chunkError(e.message)}n&&0===t.status&&this._chunkError()}},this._chunkLoaded=function(){4===t.readyState&&(t.status<200||400<=t.status?this._chunkError():(this._start+=this._config.chunkSize?this._config.chunkSize:t.responseText.length,this._finished=!this._config.chunkSize||this._start>=function(e){var t=e.getResponseHeader("Content-Range");return null===t?-1:parseInt(t.substring(t.lastIndexOf("/")+1))}(t),this.parseChunk(t.responseText)))},this._chunkError=function(e){var n=t.statusText||e;this._sendError(new Error(n))}}function c(e){var t,n;(e=e||{}).chunkSize||(e.chunkSize=a.LocalChunkSize),u.call(this,e);var r="undefined"!=typeof FileReader;this.stream=function(e){this._input=e,n=e.slice||e.webkitSlice||e.mozSlice,r?((t=new FileReader).onload=b(this._chunkLoaded,this),t.onerror=b(this._chunkError,this)):t=new FileReaderSync,this._nextChunk()},this._nextChunk=function(){this._finished||this._config.preview&&!(this._rowCount<this._config.preview)||this._readChunk()},this._readChunk=function(){var e=this._input;if(this._config.chunkSize){var i=Math.min(this._start+this._config.chunkSize,this._input.size);e=n.call(e,this._start,i)}var s=t.readAsText(e,this._config.encoding);r||this._chunkLoaded({target:{result:s}})},this._chunkLoaded=function(e){this._start+=this._config.chunkSize,this._finished=!this._config.chunkSize||this._start>=this._input.size,this.parseChunk(e.target.result)},this._chunkError=function(){this._sendError(t.error)}}function f(e){var t;u.call(this,e=e||{}),this.stream=function(e){return t=e,this._nextChunk()},this._nextChunk=function(){if(!this._finished){var e,n=this._config.chunkSize;return n?(e=t.substring(0,n),t=t.substring(n)):(e=t,t=""),this._finished=!t,this.parseChunk(e)}}}function d(e){u.call(this,e=e||{});var t=[],n=!0,r=!1;this.pause=function(){u.prototype.pause.apply(this,arguments),this._input.pause()},this.resume=function(){u.prototype.resume.apply(this,arguments),this._input.resume()},this.stream=function(e){this._input=e,this._input.on("data",this._streamData),this._input.on("end",this._streamEnd),this._input.on("error",this._streamError)},this._checkIsFinished=function(){r&&1===t.length&&(this._finished=!0)},this._nextChunk=function(){this._checkIsFinished(),t.length?this.parseChunk(t.shift()):n=!0},this._streamData=b((function(e){try{t.push("string"==typeof e?e:e.toString(this._config.encoding)),n&&(n=!1,this._checkIsFinished(),this.parseChunk(t.shift()))}catch(e){this._streamError(e)}}),this),this._streamError=b((function(e){this._streamCleanUp(),this._sendError(e)}),this),this._streamEnd=b((function(){this._streamCleanUp(),r=!0,this._streamData("")}),this),this._streamCleanUp=b((function(){this._input.removeListener("data",this._streamData),this._input.removeListener("end",this._streamEnd),this._input.removeListener("error",this._streamError)}),this)}function h(e){var t,n,r,i=Math.pow(2,53),s=-i,o=/^\s*-?(\d+\.?|\.\d+|\d+\.\d+)([eE][-+]?\d+)?\s*$/,u=/^(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))$/,l=this,c=0,f=0,d=!1,h=!1,g=[],_={data:[],errors:[],meta:{}};if(w(e.step)){var y=e.step;e.step=function(t){if(_=t,E())k();else{if(k(),0===_.data.length)return;c+=t.data.length,e.preview&&c>e.preview?n.abort():(_.data=_.data[0],y(_,l))}}}function b(t){return"greedy"===e.skipEmptyLines?""===t.join("").trim():1===t.length&&0===t[0].length}function k(){return _&&r&&(O("Delimiter","UndetectableDelimiter","Unable to auto-detect delimiting character; defaulted to '"+a.DefaultDelimiter+"'"),r=!1),e.skipEmptyLines&&(_.data=_.data.filter((function(e){return!b(e)}))),E()&&function(){if(_)if(Array.isArray(_.data[0])){for(var t=0;E()&&t<_.data.length;t++)_.data[t].forEach(n);_.data.splice(0,1)}else _.data.forEach(n);function n(t,n){w(e.transformHeader)&&(t=e.transformHeader(t,n)),g.push(t)}}(),function(){if(!_||!e.header&&!e.dynamicTyping&&!e.transform)return _;function t(t,n){var r,i=e.header?{}:[];for(r=0;r<t.length;r++){var s=r,a=t[r];e.header&&(s=r>=g.length?"__parsed_extra":g[r]),e.transform&&(a=e.transform(a,s)),a=C(s,a),"__parsed_extra"===s?(i[s]=i[s]||[],i[s].push(a)):i[s]=a}return e.header&&(r>g.length?O("FieldMismatch","TooManyFields","Too many fields: expected "+g.length+" fields but parsed "+r,f+n):r<g.length&&O("FieldMismatch","TooFewFields","Too few fields: expected "+g.length+" fields but parsed "+r,f+n)),i}var n=1;return!_.data.length||Array.isArray(_.data[0])?(_.data=_.data.map(t),n=_.data.length):_.data=t(_.data,0),e.header&&_.meta&&(_.meta.fields=g),f+=n,_}()}function E(){return e.header&&0===g.length}function C(t,n){return r=t,e.dynamicTypingFunction&&void 0===e.dynamicTyping[r]&&(e.dynamicTyping[r]=e.dynamicTypingFunction(r)),!0===(e.dynamicTyping[r]||e.dynamicTyping)?"true"===n||"TRUE"===n||"false"!==n&&"FALSE"!==n&&(function(e){if(o.test(e)){var t=parseFloat(e);if(s<t&&t<i)return!0}return!1}(n)?parseFloat(n):u.test(n)?new Date(n):""===n?null:n):n;var r}function O(e,t,n,r){var i={type:e,code:t,message:n};void 0!==r&&(i.row=r),_.errors.push(i)}this.parse=function(i,s,o){var u=e.quoteChar||'"';if(e.newline||(e.newline=function(e,t){e=e.substring(0,1048576);var n=new RegExp(p(t)+"([^]*?)"+p(t),"gm"),r=(e=e.replace(n,"")).split("\r"),i=e.split("\n"),s=1<i.length&&i[0].length<r[0].length;if(1===r.length||s)return"\n";for(var a=0,o=0;o<r.length;o++)"\n"===r[o][0]&&a++;return a>=r.length/2?"\r\n":"\r"}(i,u)),r=!1,e.delimiter)w(e.delimiter)&&(e.delimiter=e.delimiter(i),_.meta.delimiter=e.delimiter);else{var l=function(t,n,r,i,s){var o,u,l,c;s=s||[",","\t","|",";",a.RECORD_SEP,a.UNIT_SEP];for(var f=0;f<s.length;f++){var d=s[f],h=0,p=0,g=0;l=void 0;for(var _=new m({comments:i,delimiter:d,newline:n,preview:10}).parse(t),y=0;y<_.data.length;y++)if(r&&b(_.data[y]))g++;else{var v=_.data[y].length;p+=v,void 0!==l?0<v&&(h+=Math.abs(v-l),l=v):l=v}0<_.data.length&&(p/=_.data.length-g),(void 0===u||h<=u)&&(void 0===c||c<p)&&1.99<p&&(u=h,o=d,c=p)}return{successful:!!(e.delimiter=o),bestDelimiter:o}}(i,e.newline,e.skipEmptyLines,e.comments,e.delimitersToGuess);l.successful?e.delimiter=l.bestDelimiter:(r=!0,e.delimiter=a.DefaultDelimiter),_.meta.delimiter=e.delimiter}var c=v(e);return e.preview&&e.header&&c.preview++,t=i,n=new m(c),_=n.parse(t,s,o),k(),d?{meta:{paused:!0}}:_||{meta:{paused:!1}}},this.paused=function(){return d},this.pause=function(){d=!0,n.abort(),t=w(e.chunk)?"":t.substring(n.getCharIndex())},this.resume=function(){l.streamer._halted?(d=!1,l.streamer.parseChunk(t,!0)):setTimeout(l.resume,3)},this.aborted=function(){return h},this.abort=function(){h=!0,n.abort(),_.meta.aborted=!0,w(e.complete)&&e.complete(_),t=""}}function p(e){return e.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")}function m(e){var t,n=(e=e||{}).delimiter,r=e.newline,i=e.comments,s=e.step,o=e.preview,u=e.fastMode,l=t=void 0===e.quoteChar||null===e.quoteChar?'"':e.quoteChar;if(void 0!==e.escapeChar&&(l=e.escapeChar),("string"!=typeof n||-1<a.BAD_DELIMITERS.indexOf(n))&&(n=","),i===n)throw new Error("Comment character same as delimiter");!0===i?i="#":("string"!=typeof i||-1<a.BAD_DELIMITERS.indexOf(i))&&(i=!1),"\n"!==r&&"\r"!==r&&"\r\n"!==r&&(r="\n");var c=0,f=!1;this.parse=function(e,a,d){if("string"!=typeof e)throw new Error("Input must be a string");var h=e.length,m=n.length,g=r.length,_=i.length,y=w(s),v=[],b=[],k=[],E=c=0;if(!e)return F();if(u||!1!==u&&-1===e.indexOf(t)){for(var C=e.split(r),O=0;O<C.length;O++){if(k=C[O],c+=k.length,O!==C.length-1)c+=r.length;else if(d)return F();if(!i||k.substring(0,_)!==i){if(y){if(v=[],A(k.split(n)),P(),f)return F()}else A(k.split(n));if(o&&o<=O)return v=v.slice(0,o),F(!0)}}return F()}for(var R=e.indexOf(n,c),S=e.indexOf(r,c),x=new RegExp(p(l)+p(t),"g"),D=e.indexOf(t,c);;)if(e[c]!==t)if(i&&0===k.length&&e.substring(c,c+_)===i){if(-1===S)return F();c=S+g,S=e.indexOf(r,c),R=e.indexOf(n,c)}else if(-1!==R&&(R<S||-1===S))k.push(e.substring(c,R)),c=R+m,R=e.indexOf(n,c);else{if(-1===S)break;if(k.push(e.substring(c,S)),M(S+g),y&&(P(),f))return F();if(o&&v.length>=o)return F(!0)}else for(D=c,c++;;){if(-1===(D=e.indexOf(t,D+1)))return d||b.push({type:"Quotes",code:"MissingQuotes",message:"Quoted field unterminated",row:v.length,index:c}),L();if(D===h-1)return L(e.substring(c,D).replace(x,t));if(t!==l||e[D+1]!==l){if(t===l||0===D||e[D-1]!==l){-1!==R&&R<D+1&&(R=e.indexOf(n,D+1)),-1!==S&&S<D+1&&(S=e.indexOf(r,D+1));var T=j(-1===S?R:Math.min(R,S));if(e.substr(D+1+T,m)===n){k.push(e.substring(c,D).replace(x,t)),e[c=D+1+T+m]!==t&&(D=e.indexOf(t,c)),R=e.indexOf(n,c),S=e.indexOf(r,c);break}var I=j(S);if(e.substring(D+1+I,D+1+I+g)===r){if(k.push(e.substring(c,D).replace(x,t)),M(D+1+I+g),R=e.indexOf(n,c),D=e.indexOf(t,c),y&&(P(),f))return F();if(o&&v.length>=o)return F(!0);break}b.push({type:"Quotes",code:"InvalidQuotes",message:"Trailing quote on quoted field is malformed",row:v.length,index:c}),D++}}else D++}return L();function A(e){v.push(e),E=c}function j(t){var n=0;if(-1!==t){var r=e.substring(D+1,t);r&&""===r.trim()&&(n=r.length)}return n}function L(t){return d||(void 0===t&&(t=e.substring(c)),k.push(t),c=h,A(k),y&&P()),F()}function M(t){c=t,A(k),k=[],S=e.indexOf(r,c)}function F(e){return{data:v,errors:b,meta:{delimiter:n,linebreak:r,aborted:f,truncated:!!e,cursor:E+(a||0)}}}function P(){s(F()),v=[],b=[]}},this.abort=function(){f=!0},this.getCharIndex=function(){return c}}function g(e){var t=e.data,n=i[t.workerId],r=!1;if(t.error)n.userError(t.error,t.file);else if(t.results&&t.results.data){var s={abort:function(){r=!0,_(t.workerId,{data:[],errors:[],meta:{aborted:!0}})},pause:y,resume:y};if(w(n.userStep)){for(var a=0;a<t.results.data.length&&(n.userStep({data:t.results.data[a],errors:t.results.errors,meta:t.results.meta},s),!r);a++);delete t.results}else w(n.userChunk)&&(n.userChunk(t.results,s,t.file),delete t.results)}t.finished&&!r&&_(t.workerId,t.results)}function _(e,t){var n=i[e];w(n.userComplete)&&n.userComplete(t),n.terminate(),delete i[e]}function y(){throw new Error("Not implemented.")}function v(e){if("object"!=typeof e||null===e)return e;var t=Array.isArray(e)?[]:{};for(var n in e)t[n]=v(e[n]);return t}function b(e,t){return function(){e.apply(t,arguments)}}function w(e){return"function"==typeof e}return r&&(t.onmessage=function(e){var n=e.data;if(void 0===a.WORKER_ID&&n&&(a.WORKER_ID=n.workerId),"string"==typeof n.input)t.postMessage({workerId:a.WORKER_ID,results:a.parse(n.input,n.config),finished:!0});else if(t.File&&n.input instanceof File||n.input instanceof Object){var r=a.parse(n.input,n.config);r&&t.postMessage({workerId:a.WORKER_ID,results:r,finished:!0})}}),(l.prototype=Object.create(u.prototype)).constructor=l,(c.prototype=Object.create(u.prototype)).constructor=c,(f.prototype=Object.create(f.prototype)).constructor=f,(d.prototype=Object.create(u.prototype)).constructor=d,a},void 0===(i="function"===typeof n?n.apply(t,r):n)||(e.exports=i)},8217:function(e,t,n){"use strict";var r=n(6086),i=n(7294);t.useSubscription=function(e){var t=e.getCurrentValue,n=e.subscribe,s=i.useState((function(){return{getCurrentValue:t,subscribe:n,value:t()}}));e=s[0];var a=s[1];return s=e.value,e.getCurrentValue===t&&e.subscribe===n||(s=t(),a({getCurrentValue:t,subscribe:n,value:s})),i.useDebugValue(s),i.useEffect((function(){function e(){if(!i){var e=t();a((function(i){return i.getCurrentValue!==t||i.subscribe!==n||i.value===e?i:r({},i,{value:e})}))}}var i=!1,s=n(e);return e(),function(){i=!0,s()}}),[t,n]),s}},7161:function(e,t,n){"use strict";e.exports=n(8217)},3481:function(e,t,n){"use strict";var r=n(7294);const i=r.forwardRef((function(e,t){return r.createElement("svg",Object.assign({xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 20 20",fill:"currentColor","aria-hidden":"true",ref:t},e),r.createElement("path",{d:"M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"}))}));t.Z=i},2659:function(e,t,n){"use strict";var r=n(7294);const i=r.forwardRef((function(e,t){return r.createElement("svg",Object.assign({xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 20 20",fill:"currentColor","aria-hidden":"true",ref:t},e),r.createElement("path",{fillRule:"evenodd",d:"M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z",clipRule:"evenodd"}))}));t.Z=i},3659:function(e,t,n){"use strict";n.d(t,{R:function(){return d}});var r={};n.r(r),n.d(r,{MDXContext:function(){return o},MDXProvider:function(){return f},useMDXComponents:function(){return l},withMDXComponents:function(){return u}});var i=n(7294),s=n(5893),a=n.t(s,2);const o=i.createContext({});function u(e){return function(t){const n=l(t.components);return i.createElement(e,{...t,allComponents:n})}}function l(e){const t=i.useContext(o);return i.useMemo((()=>"function"===typeof e?e(t):{...t,...e}),[t,e])}const c={};function f({components:e,children:t,disableParentContext:n}){let r=l(e);return n&&(r=e||c),i.createElement(o.Provider,{value:r},t)}function d({compiledSource:e,frontmatter:t,scope:n,components:s={},lazy:o}){const[u,l]=(0,i.useState)(!o||"undefined"===typeof window);(0,i.useEffect)((()=>{if(o){const e=window.requestIdleCallback((()=>{l(!0)}));return()=>window.cancelIdleCallback(e)}}),[]);const c=(0,i.useMemo)((()=>{const i=Object.assign({opts:{...r,...a}},{frontmatter:t},n),s=Object.keys(i),o=Object.values(i),u=Reflect.construct(Function,s.concat(`${e}`));return u.apply(u,o).default}),[n,e]);if(!u)return i.createElement("div",{dangerouslySetInnerHTML:{__html:""},suppressHydrationWarning:!0});const d=i.createElement(f,{components:s},i.createElement(c,null));return o?i.createElement("div",null,d):d}"undefined"!==typeof window&&(window.requestIdleCallback=window.requestIdleCallback||function(e){var t=Date.now();return setTimeout((function(){e({didTimeout:!1,timeRemaining:function(){return Math.max(0,50-(Date.now()-t))}})}),1)},window.cancelIdleCallback=window.cancelIdleCallback||function(e){clearTimeout(e)})}}]);