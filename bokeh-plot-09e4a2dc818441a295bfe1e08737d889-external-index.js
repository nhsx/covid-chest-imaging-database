(function() {
  var fn = function() {
    
    (function(root) {
      function now() {
        return new Date();
      }
    
      var force = false;
    
      if (typeof root._bokeh_onload_callbacks === "undefined" || force === true) {
        root._bokeh_onload_callbacks = [];
        root._bokeh_is_loading = undefined;
      }
    
      
      
    
      var element = document.getElementById("ade3591b-81b9-4f42-b7a9-7d4d04576748");
        if (element == null) {
          console.warn("Bokeh: autoload.js configured with elementid 'ade3591b-81b9-4f42-b7a9-7d4d04576748' but no matching script tag was found.")
        }
      
    
      function run_callbacks() {
        try {
          root._bokeh_onload_callbacks.forEach(function(callback) {
            if (callback != null)
              callback();
          });
        } finally {
          delete root._bokeh_onload_callbacks
        }
        console.debug("Bokeh: all callbacks have finished");
      }
    
      function load_libs(css_urls, js_urls, callback) {
        if (css_urls == null) css_urls = [];
        if (js_urls == null) js_urls = [];
    
        root._bokeh_onload_callbacks.push(callback);
        if (root._bokeh_is_loading > 0) {
          console.debug("Bokeh: BokehJS is being loaded, scheduling callback at", now());
          return null;
        }
        if (js_urls == null || js_urls.length === 0) {
          run_callbacks();
          return null;
        }
        console.debug("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
        root._bokeh_is_loading = css_urls.length + js_urls.length;
    
        function on_load() {
          root._bokeh_is_loading--;
          if (root._bokeh_is_loading === 0) {
            console.debug("Bokeh: all BokehJS libraries/stylesheets loaded");
            run_callbacks()
          }
        }
    
        function on_error() {
          console.error("failed to load " + url);
        }
    
        for (var i = 0; i < css_urls.length; i++) {
          var url = css_urls[i];
          const element = document.createElement("link");
          element.onload = on_load;
          element.onerror = on_error;
          element.rel = "stylesheet";
          element.type = "text/css";
          element.href = url;
          console.debug("Bokeh: injecting link tag for BokehJS stylesheet: ", url);
          document.body.appendChild(element);
        }
    
        const hashes = {"https://cdn.bokeh.org/bokeh/release/bokeh-2.0.2.min.js": "ufR9RFnRs6lniiaFvtJziE0YeidtAgBRH6ux2oUItHw5WTvE1zuk9uzhUU/FJXDp", "https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.0.2.min.js": "8QM/PGWBT+IssZuRcDcjzwIh1mkOmJSoNMmyYDZbCfXJg3Ap1lEvdVgFuSAwhb/J", "https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.0.2.min.js": "Jm8cH3Rg0P6UeZhVY5cLy1WzKajUT9KImCY+76hEqrcJt59/d8GPvFHjCkYgnSIn", "https://cdn.bokeh.org/bokeh/release/bokeh-gl-2.0.2.min.js": "Ozhzj+SI7ywm74aOI/UajcWz+C0NjsPunEVyVIrxzYkB+jA+2tUw8x5xJCbVtK5I"};
    
        for (var i = 0; i < js_urls.length; i++) {
          var url = js_urls[i];
          var element = document.createElement('script');
          element.onload = on_load;
          element.onerror = on_error;
          element.async = false;
          element.src = url;
          if (url in hashes) {
            element.crossOrigin = "anonymous";
            element.integrity = "sha384-" + hashes[url];
          }
          console.debug("Bokeh: injecting script tag for BokehJS library: ", url);
          document.head.appendChild(element);
        }
      };
    
      function inject_raw_css(css) {
        const element = document.createElement("style");
        element.appendChild(document.createTextNode(css));
        document.body.appendChild(element);
      }
    
      
      var js_urls = ["https://cdn.bokeh.org/bokeh/release/bokeh-2.0.2.min.js", "https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.0.2.min.js", "https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.0.2.min.js", "https://cdn.bokeh.org/bokeh/release/bokeh-gl-2.0.2.min.js"];
      var css_urls = [];
      
    
      var inline_js = [
        function(Bokeh) {
          Bokeh.set_log_level("info");
        },
        
        function(Bokeh) {
          (function() {
            var fn = function() {
              Bokeh.safely(function() {
                (function(root) {
                  function embed_document(root) {
                    
                  var docs_json = '{&quot;67adcdfc-9ce9-47b6-a657-e391a5b8d714&quot;:{&quot;roots&quot;:{&quot;references&quot;:[{&quot;attributes&quot;:{&quot;tile_source&quot;:{&quot;id&quot;:&quot;1001&quot;}},&quot;id&quot;:&quot;1044&quot;,&quot;type&quot;:&quot;TileRenderer&quot;},{&quot;attributes&quot;:{&quot;data_source&quot;:{&quot;id&quot;:&quot;1002&quot;},&quot;glyph&quot;:{&quot;id&quot;:&quot;1047&quot;},&quot;hover_glyph&quot;:null,&quot;muted_glyph&quot;:null,&quot;nonselection_glyph&quot;:{&quot;id&quot;:&quot;1048&quot;},&quot;selection_glyph&quot;:null,&quot;view&quot;:{&quot;id&quot;:&quot;1050&quot;}},&quot;id&quot;:&quot;1049&quot;,&quot;type&quot;:&quot;GlyphRenderer&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1010&quot;,&quot;type&quot;:&quot;LinearScale&quot;},{&quot;attributes&quot;:{&quot;below&quot;:[{&quot;id&quot;:&quot;1012&quot;}],&quot;center&quot;:[{&quot;id&quot;:&quot;1019&quot;},{&quot;id&quot;:&quot;1027&quot;}],&quot;left&quot;:[{&quot;id&quot;:&quot;1020&quot;}],&quot;renderers&quot;:[{&quot;id&quot;:&quot;1044&quot;},{&quot;id&quot;:&quot;1049&quot;}],&quot;sizing_mode&quot;:&quot;scale_both&quot;,&quot;title&quot;:{&quot;id&quot;:&quot;1055&quot;},&quot;toolbar&quot;:{&quot;id&quot;:&quot;1036&quot;},&quot;toolbar_location&quot;:null,&quot;x_range&quot;:{&quot;id&quot;:&quot;1004&quot;},&quot;x_scale&quot;:{&quot;id&quot;:&quot;1008&quot;},&quot;y_range&quot;:{&quot;id&quot;:&quot;1006&quot;},&quot;y_scale&quot;:{&quot;id&quot;:&quot;1010&quot;}},&quot;id&quot;:&quot;1003&quot;,&quot;subtype&quot;:&quot;Figure&quot;,&quot;type&quot;:&quot;Plot&quot;},{&quot;attributes&quot;:{&quot;dimension&quot;:&quot;lat&quot;},&quot;id&quot;:&quot;1021&quot;,&quot;type&quot;:&quot;MercatorTicker&quot;},{&quot;attributes&quot;:{&quot;bottom_units&quot;:&quot;screen&quot;,&quot;fill_alpha&quot;:0.5,&quot;fill_color&quot;:&quot;lightgrey&quot;,&quot;left_units&quot;:&quot;screen&quot;,&quot;level&quot;:&quot;overlay&quot;,&quot;line_alpha&quot;:1.0,&quot;line_color&quot;:&quot;black&quot;,&quot;line_dash&quot;:[4,4],&quot;line_width&quot;:2,&quot;render_mode&quot;:&quot;css&quot;,&quot;right_units&quot;:&quot;screen&quot;,&quot;top_units&quot;:&quot;screen&quot;},&quot;id&quot;:&quot;1034&quot;,&quot;type&quot;:&quot;BoxAnnotation&quot;},{&quot;attributes&quot;:{&quot;end&quot;:109296.15612735572,&quot;start&quot;:-1223904.361365029},&quot;id&quot;:&quot;1004&quot;,&quot;type&quot;:&quot;Range1d&quot;},{&quot;attributes&quot;:{&quot;formatter&quot;:{&quot;id&quot;:&quot;1015&quot;},&quot;ticker&quot;:{&quot;id&quot;:&quot;1013&quot;},&quot;visible&quot;:false},&quot;id&quot;:&quot;1012&quot;,&quot;type&quot;:&quot;MercatorAxis&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1008&quot;,&quot;type&quot;:&quot;LinearScale&quot;},{&quot;attributes&quot;:{&quot;end&quot;:8610142.253916021,&quot;start&quot;:6380612.411463196},&quot;id&quot;:&quot;1006&quot;,&quot;type&quot;:&quot;Range1d&quot;},{&quot;attributes&quot;:{&quot;dimension&quot;:&quot;lon&quot;},&quot;id&quot;:&quot;1013&quot;,&quot;type&quot;:&quot;MercatorTicker&quot;},{&quot;attributes&quot;:{&quot;dimension&quot;:&quot;lon&quot;},&quot;id&quot;:&quot;1015&quot;,&quot;type&quot;:&quot;MercatorTickFormatter&quot;},{&quot;attributes&quot;:{&quot;axis&quot;:{&quot;id&quot;:&quot;1012&quot;},&quot;ticker&quot;:null},&quot;id&quot;:&quot;1019&quot;,&quot;type&quot;:&quot;Grid&quot;},{&quot;attributes&quot;:{&quot;formatter&quot;:{&quot;id&quot;:&quot;1023&quot;},&quot;ticker&quot;:{&quot;id&quot;:&quot;1021&quot;},&quot;visible&quot;:false},&quot;id&quot;:&quot;1020&quot;,&quot;type&quot;:&quot;MercatorAxis&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1028&quot;,&quot;type&quot;:&quot;PanTool&quot;},{&quot;attributes&quot;:{&quot;attribution&quot;:&quot;&amp;copy; &lt;a href=\\&quot;https://www.openstreetmap.org/copyright\\&quot;&gt;OpenStreetMap&lt;/a&gt; contributors,&amp;copy; &lt;a href=\\&quot;https://cartodb.com/attributions\\&quot;&gt;CartoDB&lt;/a&gt;&quot;,&quot;url&quot;:&quot;https://tiles.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png&quot;},&quot;id&quot;:&quot;1001&quot;,&quot;type&quot;:&quot;WMTSTileSource&quot;},{&quot;attributes&quot;:{&quot;dimension&quot;:&quot;lat&quot;},&quot;id&quot;:&quot;1023&quot;,&quot;type&quot;:&quot;MercatorTickFormatter&quot;},{&quot;attributes&quot;:{&quot;axis&quot;:{&quot;id&quot;:&quot;1020&quot;},&quot;dimension&quot;:1,&quot;ticker&quot;:null},&quot;id&quot;:&quot;1027&quot;,&quot;type&quot;:&quot;Grid&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1029&quot;,&quot;type&quot;:&quot;WheelZoomTool&quot;},{&quot;attributes&quot;:{&quot;callback&quot;:null,&quot;tooltips&quot;:&quot;\\n    &lt;div class=\\&quot;tooltip\\&quot;&gt;\\n        &lt;span style=\\&quot;font-size: 15px; font-weight: bold; font-family: Furtiger W01,Arial,Sans-serif;\\&quot;&gt;@name&lt;/span&gt;\\n    &lt;/div&gt;\\n&quot;},&quot;id&quot;:&quot;1035&quot;,&quot;type&quot;:&quot;HoverTool&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1033&quot;,&quot;type&quot;:&quot;HelpTool&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1061&quot;,&quot;type&quot;:&quot;UnionRenderers&quot;},{&quot;attributes&quot;:{&quot;overlay&quot;:{&quot;id&quot;:&quot;1034&quot;}},&quot;id&quot;:&quot;1030&quot;,&quot;type&quot;:&quot;BoxZoomTool&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1031&quot;,&quot;type&quot;:&quot;SaveTool&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1062&quot;,&quot;type&quot;:&quot;Selection&quot;},{&quot;attributes&quot;:{},&quot;id&quot;:&quot;1032&quot;,&quot;type&quot;:&quot;ResetTool&quot;},{&quot;attributes&quot;:{&quot;fill_alpha&quot;:{&quot;value&quot;:0.1},&quot;fill_color&quot;:{&quot;value&quot;:&quot;#003087&quot;},&quot;line_alpha&quot;:{&quot;value&quot;:0.1},&quot;line_color&quot;:{&quot;value&quot;:&quot;Black&quot;},&quot;size&quot;:{&quot;units&quot;:&quot;screen&quot;,&quot;value&quot;:8},&quot;x&quot;:{&quot;field&quot;:&quot;x&quot;},&quot;y&quot;:{&quot;field&quot;:&quot;y&quot;}},&quot;id&quot;:&quot;1048&quot;,&quot;type&quot;:&quot;Circle&quot;},{&quot;attributes&quot;:{&quot;text&quot;:&quot;&quot;},&quot;id&quot;:&quot;1055&quot;,&quot;type&quot;:&quot;Title&quot;},{&quot;attributes&quot;:{&quot;fill_color&quot;:{&quot;value&quot;:&quot;#003087&quot;},&quot;line_color&quot;:{&quot;value&quot;:&quot;Black&quot;},&quot;size&quot;:{&quot;units&quot;:&quot;screen&quot;,&quot;value&quot;:8},&quot;x&quot;:{&quot;field&quot;:&quot;x&quot;},&quot;y&quot;:{&quot;field&quot;:&quot;y&quot;}},&quot;id&quot;:&quot;1047&quot;,&quot;type&quot;:&quot;Circle&quot;},{&quot;attributes&quot;:{&quot;active_drag&quot;:null,&quot;active_inspect&quot;:&quot;auto&quot;,&quot;active_multi&quot;:null,&quot;active_scroll&quot;:null,&quot;active_tap&quot;:null,&quot;tools&quot;:[{&quot;id&quot;:&quot;1028&quot;},{&quot;id&quot;:&quot;1029&quot;},{&quot;id&quot;:&quot;1030&quot;},{&quot;id&quot;:&quot;1031&quot;},{&quot;id&quot;:&quot;1032&quot;},{&quot;id&quot;:&quot;1033&quot;},{&quot;id&quot;:&quot;1035&quot;}]},&quot;id&quot;:&quot;1036&quot;,&quot;type&quot;:&quot;Toolbar&quot;},{&quot;attributes&quot;:{&quot;data&quot;:{&quot;name&quot;:[&quot;Royal United Hospitals Bath NHS Foundation Trust&quot;,&quot;Brighton and Sussex University Hospitals NHS Trust&quot;,&quot;London North West University Healthcare NHS Trust&quot;,&quot;George Eliot Hospital NHS Trust&quot;,&quot;Cwm Taf Morgannwg University Health Board&quot;,&quot;Hampshire Hospitals NHS Foundation Trust&quot;,&quot;Betsi Cadwaladr University Health Board&quot;,&quot;Ashford and St Peter&#x27;s Hospitals&quot;,&quot;Royal Cornwall Hospitals NHS Trust&quot;,&quot;Sheffield Children\\u2019s NHS Foundation Trust&quot;,&quot;Liverpool Heart and Chest Hospital NHS Foundation Trust&quot;,&quot;Norfolk and Norwich University Hospitals NHS Foundation Trust&quot;,&quot;Royal Surrey NHS Foundation Trust&quot;,&quot;Sandwell and West Birmingham NHS Trust&quot;,&quot;West Suffolk NHS Foundation Trust&quot;,&quot;Somerset NHS Foundation Trust&quot;,&quot;Cambridge University Hospitals NHS Foundation Trust&quot;,&quot;Imperial College Healthcare NHS Trust&quot;,&quot;Oxford University Hospitals NHS Foundation Trust&quot;],&quot;x&quot;:[-266496.40079835034,-13343.566798764561,-30210.6849118123,-164758.04499426493,-377204.0796702241,-148203.70125449906,-463290.870540979,-115030.83808852501,-566863.114768342,-165799.13826801084,-322780.437031305,135833.26718035116,-67673.56748202846,-222969.3778352216,79036.72714373344,-347176.2147581416,15659.758047852967,-19402.987245267585,-166871.59024231325],&quot;y&quot;:[6690927.773689134,6589464.980535217,6715805.116747058,6893308.82239866,6757594.82625833,6632180.765754477,7021657.951376161,6700219.378753096,6492542.704073475,7053716.315047512,7059600.8274308145,6912530.048599514,6664080.402738612,6895315.619411273,6842133.424528319,6623430.282307182,6831881.4946985105,6713441.740310962,6757635.2424149765]},&quot;selected&quot;:{&quot;id&quot;:&quot;1062&quot;},&quot;selection_policy&quot;:{&quot;id&quot;:&quot;1061&quot;}},&quot;id&quot;:&quot;1002&quot;,&quot;type&quot;:&quot;ColumnDataSource&quot;},{&quot;attributes&quot;:{&quot;source&quot;:{&quot;id&quot;:&quot;1002&quot;}},&quot;id&quot;:&quot;1050&quot;,&quot;type&quot;:&quot;CDSView&quot;}],&quot;root_ids&quot;:[&quot;1003&quot;]},&quot;title&quot;:&quot;Bokeh Application&quot;,&quot;version&quot;:&quot;2.0.2&quot;}}';
                  var render_items = [{"docid":"67adcdfc-9ce9-47b6-a657-e391a5b8d714","root_ids":["1003"],"roots":{"1003":"ade3591b-81b9-4f42-b7a9-7d4d04576748"}}];
                  root.Bokeh.embed.embed_items(docs_json, render_items);
                
                  }
                  if (root.Bokeh !== undefined) {
                    embed_document(root);
                  } else {
                    var attempts = 0;
                    var timer = setInterval(function(root) {
                      if (root.Bokeh !== undefined) {
                        clearInterval(timer);
                        embed_document(root);
                      } else {
                        attempts++;
                        if (attempts > 100) {
                          clearInterval(timer);
                          console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing");
                        }
                      }
                    }, 10, root)
                  }
                })(window);
              });
            };
            if (document.readyState != "loading") fn();
            else document.addEventListener("DOMContentLoaded", fn);
          })();
        },
        function(Bokeh) {
        
        
        }
      ];
    
      function run_inline_js() {
        
        for (var i = 0; i < inline_js.length; i++) {
          inline_js[i].call(root, root.Bokeh);
        }
        
      }
    
      if (root._bokeh_is_loading === 0) {
        console.debug("Bokeh: BokehJS loaded, going straight to plotting");
        run_inline_js();
      } else {
        load_libs(css_urls, js_urls, function() {
          console.debug("Bokeh: BokehJS plotting callback run at", now());
          run_inline_js();
        });
      }
    }(window));
  };
  if (document.readyState != "loading") fn();
  else document.addEventListener("DOMContentLoaded", fn);
})();