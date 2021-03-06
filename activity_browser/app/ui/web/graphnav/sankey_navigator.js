

console.log ("Starting Sankey Navigator.");

//var heading = document.getElementById("heading");
// document.getElementById("data").innerHTML = "no data yet";

// SETUP GRAPH
// https://github.com/dagrejs/graphlib/wiki/API-Reference
// HOW TO SET EDGES AND NODES MANUALLY USING GRAPHLIB:
// digraph.setNode("kspacey",    { label: "Kevin Spacey",  width: 144, height: 100 });
// digraph.setEdge("kspacey",   "swilliams");
// var graph = new dagre.graphlib.Graph({ multigraph: true });

// Set an object for the graph label
// graph.setGraph({});


// Create and configure the renderer
// var render = dagreD3.render();


function getWindowSize() {
    w = window,
    d = document,
    e = d.documentElement,
    g = d.getElementsByTagName('body')[0],
    x = w.innerWidth ; //|| e.clientWidth || g.clientWidth;
    y = w.innerHeight ; //|| e.clientHeight || g.clientHeight;

    //preventing the svg canvas to be 0x0, as page is loaded in the background with dimensions 0x0
    if (x,y == 0) {
        x = 600;
        y = 500;
    };

    globalWidth = x;
    globalHeight = y;
    return {x,y};
};


var globalWidth = null;
var globalHeight = null;

// initialize panCanvas (container actually displaying graph) globally, to enable node-info extraction on-click
var panCanvas = {};

/*
BEGIN OF ADAPTED DEMO CODE FROM BILL WHITE D3 PAN AND ZOOM DEMOS
http://www.billdwhite.com/wordpress/2017/09/
http://www.billdwhite.com/wordpress/2014/02/03/d3-pan-and-zoom-reuse-demo/
http://www.billdwhite.com/wordpress/2013/12/02/d3-force-layout-with-pan-and-zoom-minimap/
*/


d3.demo = {};

/** CANVAS **/
// function object for the canvas
d3.demo.canvas = function() {

    getWindowSize();

    "use strict";
    console.log("w: "+globalWidth+ " ; h: "+globalHeight)
    var width           = globalWidth*0.9,
        height          = globalHeight*0.6,
        base            = null,
        wrapperBorder   = 0,
        minimap         = null,
        minimapPadding  = 10,
        minimapScale    = 0.1; //reduced minimap scale to (help) prevent graph to exceed panel size

    //introduced function to reset width/height according to new window sizes
    updateDimensions = function() {
        getWindowSize();
        width           = globalWidth*0.99;
        height          = globalHeight*0.6;
    }


    function canvas(selection) {

        base = selection;
        //changed location of MiniMap to under the graph for better layout with very wide graphs
        var svgWidth = (width  + (wrapperBorder*2) + minimapPadding*2);
        var svgHeight = (height + (wrapperBorder*2) + minimapPadding*2 + (height*minimapScale));
        var svg = selection.append("svg")
            .attr("class", "svg canvas")
            .attr("width", svgWidth)
            .attr("height", svgHeight)
            .attr("shape-rendering", "auto");

        var svgDefs = svg.append("defs");
        svgDefs.append("clipPath")
            .attr("id", "wrapperClipPath_qwpyza")
            .attr("class", "wrapper clipPath")
            .append("rect")
            .attr("class", "background")
            .attr("width", width)
            .attr("height", height);
        svgDefs.append("clipPath")
            .attr("id", "minimapClipPath_qwpyza")
            .attr("class", "minimap clipPath")
            .attr("width", width)
            .attr("height", height)
            .append("rect")
            .attr("class", "background")
            .attr("width", width)
            .attr("height", height);

        var filter = svgDefs.append("svg:filter")  // frame of the mini-map
            .attr("id", "minimapDropShadow_qwpyza")
            .attr("x", "-20%")
            .attr("y", "-20%")
            .attr("width", "150%")
            .attr("height", "150%");
        filter.append("svg:feOffset")
            .attr("result", "offOut")
            .attr("in", "SourceGraphic")
            .attr("dx", "1")
            .attr("dy", "1");
        filter.append("svg:feColorMatrix")
            .attr("result", "matrixOut")
            .attr("in", "offOut")
            .attr("type", "matrix")
            .attr("values", "0.1 0 0 0 0 0 0.1 0 0 0 0 0 0.1 0 0 0 0 0 0.5 0");
        filter.append("svg:feGaussianBlur")
            .attr("result", "blurOut")
            .attr("in", "matrixOut")
            .attr("stdDeviation", "10");
        filter.append("svg:feBlend")
            .attr("in", "SourceGraphic")
            .attr("in2", "blurOut")
            .attr("mode", "normal");

        var minimapRadialFill = svgDefs.append("radialGradient")
            .attr('id', "minimapGradient")
            .attr('gradientUnits', "userSpaceOnUse")
            .attr('cx', "500")
            .attr('cy', "500")
            .attr('r', "400")
            .attr('fx', "500")
            .attr('fy', "500");
        minimapRadialFill.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", "#FFFFFF");
        minimapRadialFill.append("stop")
            .attr("offset", "40%")
            .attr("stop-color", "#EEEEEE")
        minimapRadialFill.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", "#E0E0E0");

        var outerWrapper = svg.append("g")
            .attr("class", "wrapper outer")
            .attr("transform", "translate(0, " + minimapPadding + ")");
        outerWrapper.append("rect")
            .attr("class", "background")
            .attr("width", width + wrapperBorder*2)
            .attr("height", height + wrapperBorder*2);

        var innerWrapper = outerWrapper.append("g")
            .attr("class", "wrapper inner")
            .attr("clip-path", "url(#wrapperClipPath_qwpyza)")
            .attr("transform", "translate(" + (wrapperBorder) + "," + (wrapperBorder) + ")");

        innerWrapper.append("rect")
            .attr("class", "background")
            .attr("width", width)
            .attr("height", height);

        panCanvas = innerWrapper.append("g")
            .attr("class", "panCanvas")
            .attr("width", width)
            .attr("height", height)
            .attr("transform", "translate(0,0)");

        panCanvas.append("rect")
            .attr("class", "background")
            .attr("width", width)
            .attr("height", height);

        var zoom = d3.zoom()
            .scaleExtent([0.25, 5]);

        // updates the zoom boundaries based on the current size and scale
        var updateCanvasZoomExtents = function() {
            var scale = innerWrapper.property("__zoom").k;
            var targetWidth = svgWidth;
            var targetHeight = svgHeight;
            var viewportWidth = width;
            var viewportHeight = height;
            //DISABLED LIMITED TRANSLATION BC OF FAULTY ZOOM BEHAVIOR
            // # TODO : Find useful way of limiting translation to boundaries of own container
            //zoom.translateExtent([
            //    [-viewportWidth/scale, -viewportHeight/scale],
            //    [(viewportWidth/scale + targetWidth), (viewportHeight/scale + targetHeight)]
            //]);
        };

        var zoomHandler = function() {
            panCanvas.attr("transform", d3.event.transform);
            // here we filter out the emitting of events that originated outside of the normal ZoomBehavior; this prevents an infinite loop
            // between the host and the minimap
            if (d3.event.sourceEvent instanceof MouseEvent || d3.event.sourceEvent instanceof WheelEvent) {
                minimap.update(d3.event.transform);
            }
            updateCanvasZoomExtents();
        };

        zoom.on("zoom", zoomHandler);

        innerWrapper.call(zoom);

        // initialize the minimap, passing needed references
        //changed location of MiniMap to under the graph for better layout with very wide graphs
        minimap = d3.demo.minimap()
            .host(canvas)
            .target(panCanvas)
            .minimapScale(minimapScale)
            .x(minimapPadding)
            .y(height + 2*minimapPadding);

        svg.call(minimap);

        /** ADD SHAPE **/
        // function to update dimensions, reset the canvas (with new dimensions), render the graph in canvas & minimap
        canvas.addItem = function() {
            //canvas.render();
            updateDimensions();
            canvas.reset();
            panCanvas.call(render,graph);
            // get panCanvas width here?
            // pan to node (implement here)
            minimap.render();
        };

        /** RENDER **/
        canvas.render = function() {
        updateDimensions(); //added call to update window sizes
            svgDefs
                .select(".clipPath .background")
                .attr("width", width)
                .attr("height", height);
            //changed location of MiniMap to under the graph for better layout with very wide graphs
            svg
                .attr("width",  width  + (wrapperBorder*2) )
                .attr("height", height + (wrapperBorder*2) + minimapPadding*2 + (width*minimapScale));

            outerWrapper
                .select(".background")
                .attr("width", width + wrapperBorder*2)
                .attr("height", height + wrapperBorder*2);

            innerWrapper
                .attr("transform", "translate(" + (wrapperBorder) + "," + (wrapperBorder) + ")")
                .select(".background")
                .attr("width", width)
                .attr("height", height);

            panCanvas
                .attr("width", width)
                .attr("height", height)
                .select(".background")
                .attr("width", width)
                .attr("height", height);

            minimap
                .x(minimapPadding)
                .y(height + 2*minimapPadding)
                .render();
        };

        canvas.reset = function() {

            //svg.call(zoom.event);
            //svg.transition().duration(750).call(zoom.event);
            zoom.transform(panCanvas, d3.zoomIdentity);
            svg.property("__zoom", d3.zoomIdentity);
            minimap.update(d3.zoomIdentity);
        };

        canvas.update = function(minimapZoomTransform) {
            zoom.transform(panCanvas, minimapZoomTransform);
            // update the '__zoom' property with the new transform on the rootGroup which is where the zoomBehavior stores it since it was the
            // call target during initialization
            innerWrapper.property("__zoom", minimapZoomTransform);

            updateCanvasZoomExtents();
        };

        updateCanvasZoomExtents();
    }


    //============================================================
    // Accessors
    //============================================================

    canvas.width = function(value) {
        if (!arguments.length) return width;
        width = parseInt(value, 10);
        return this;
    };

    canvas.height = function(value) {
        if (!arguments.length) return height;
        height = parseInt(value, 10);
        return this;
    };

    return canvas;
};



/** MINIMAP **/
d3.demo.minimap = function() {

    "use strict";

    var minimapScale    = 0.1,
        host            = null,
        base            = null,
        target          = null,
        width           = 0,
        height          = 0,
        x               = 0,
        y               = 0;

    function minimap(selection) {

        base = selection;

        var zoom = d3.zoom()
            .scaleExtent([0.25, 5]);

        // updates the zoom boundaries based on the current size and scale
        var updateMinimapZoomExtents = function() {
            var scale = container.property("__zoom").k;
            var targetWidth = parseInt(target.attr("width"));
            var targetHeight = parseInt(target.attr("height"));
            var viewportWidth = host.width();
            var viewportHeight = host.height();
            //DISABLED LIMITED TRANSLATION BC OF FAULTY ZOOM BEHAVIOR
            // # TODO : Find useful way of limiting translation to boundaries of own container
            //zoom.translateExtent([
            //    [-viewportWidth/scale, -viewportHeight/scale],
            //   [(viewportWidth/scale + targetWidth), (viewportHeight/scale + targetHeight)]
            //]);
        };

        var zoomHandler = function() {
            frame.attr("transform", d3.event.transform);
            // here we filter out the emitting of events that originated outside of the normal ZoomBehavior; this prevents an infinite loop
            // between the host and the minimap
            if (d3.event.sourceEvent instanceof MouseEvent || d3.event.sourceEvent instanceof WheelEvent) {
                // invert the outgoing transform and apply it to the host
                var transform = d3.event.transform;
                // ordering matters here! you have to scale() before you translate()
                var modifiedTransform = d3.zoomIdentity.scale(1/transform.k).translate(-transform.x, -transform.y);
                host.update(modifiedTransform);
            }

            updateMinimapZoomExtents();
        };

        zoom.on("zoom", zoomHandler);

        var container = selection.append("g")
            .attr("class", "minimap");

        container.call(zoom);

        minimap.node = container.node();

        var frame = container.append("g")
            .attr("class", "frame")

        frame.append("rect")
            .attr("class", "background")
            .attr("width", width)
            .attr("height", height)
            .attr("filter", "url(#minimapDropShadow_qPWKOg)");


        minimap.update = function(hostTransform) {
            // invert the incoming zoomTransform; ordering matters here! you have to scale() before you translate()
            var modifiedTransform = d3.zoomIdentity.scale((1/hostTransform.k)).translate(-hostTransform.x, -hostTransform.y);
            // call this.zoom.transform which will reuse the handleZoom method below
            zoom.transform(frame, modifiedTransform);
            // update the new transform onto the minimapCanvas which is where the zoomBehavior stores it since it was the call target during initialization
            container.property("__zoom", modifiedTransform);

            updateMinimapZoomExtents();
        };


        /** RENDER **/
        minimap.render = function() {
            // update the placement of the minimap
            container.attr("transform", "translate(" + x + "," + y + ")scale(" + minimapScale + ")");
            // update the visualization being shown by the minimap in case its appearance has changed
            var node = target.node().cloneNode(true);
            node.removeAttribute("id");
            base.selectAll(".minimap .panCanvas").remove();
            minimap.node.appendChild(node); // minimap node is the container's node
            d3.select(node).attr("transform", "translate(0,0)");
            // keep the minimap's viewport (frame) sized to match the current visualization viewport dimensions
            frame.select(".background")
                .attr("width", width)
                .attr("height", height);
            frame.node().parentNode.appendChild(frame.node());
        };

        updateMinimapZoomExtents();
    }


    //============================================================
    // Accessors
    //============================================================


    minimap.width = function(value) {
        if (!arguments.length) return width;
        width = parseInt(value, 10);
        return this;
    };


    minimap.height = function(value) {
        if (!arguments.length) return height;
        height = parseInt(value, 10);
        return this;
    };


    minimap.x = function(value) {
        if (!arguments.length) return x;
        x = parseInt(value, 10);
        return this;
    };


    minimap.y = function(value) {
        if (!arguments.length) return y;
        y = parseInt(value, 10);
        return this;
    };


    minimap.host = function(value) {
        if (!arguments.length) { return host;}
        host = value;
        return this;
    }


    minimap.minimapScale = function(value) {
        if (!arguments.length) { return minimapScale; }
        minimapScale = value;
        return this;
    };


    minimap.target = function(value) {
        if (!arguments.length) { return target; }
        target = value;
        width  = parseInt(target.attr("width"),  10);
        height = parseInt(target.attr("height"), 10);
        return this;
    };

    return minimap;
};

/** RUN SCRIPT **/

//instantiation of canvas container+reset button
var canvas = d3.demo.canvas();
d3.select("#canvasqPWKOg").call(canvas);

d3.select("#resetButtonqPWKOg").on("click", function() {
    canvas.reset();
});

/* END OF ADAPTED DEMO SCRIPT*/



/**
 * Build svg container and listen for zoom and drag calls
 */

/*
var svg = d3.select("body")
 .append("svg")
 .attr("viewBox", "0 0 600 400")
 .attr("height", "100%")
 .attr("width", "100%")
 .call(d3.zoom().on("zoom", function () {
    svg.attr("transform", d3.event.transform)
 })) */


// Tooltip: http://bl.ocks.org/d3noob/a22c42db65eb00d4e369
var div = d3.select("#canvasqPWKOg").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

// Access graph size:
//panCanvas.graph().width

var color = d3.scaleLinear()
    .domain([-99999999, -1, 0, 1, 99999999])
    .range(["green", "green", "white", "red", "red"]);

//var color = d3.scaleLinear()
//    .domain([-1, 0, 1])
//    .range(["green", "white", "red"]);

var max_string_length = 20
var max_edge_width = 40

var render = dagreD3.render();
var graph = {}

function update_graph(json_data) {
    console.log("Updating Graph")
	data = JSON.parse(json_data)
	max_impact = data["max_impact"]
	console.log("Max impact:", max_impact)
	var graph_test = d3.select()
	    .append("svg");

	heading.innerHTML = data.title;

	// reset graph
	graph = new dagre.graphlib.Graph({ multigraph: true });
	graph.setGraph({});

    // nodes --> graph
    data.nodes.forEach(function(n) {
        graph.setNode(n['id'], {
        //	      label: formatNodeText(n), //chunkString(n['name'], max_string_length) + '\n' + n['location'],
          label: wrapText(n['name'], max_string_length)
                        + '\n' + n['location']
                        + '\n(' + Math.round(n['ind_norm'] * 100) + '%)',
//                        + '\n' + roundNumber(n['ind']) + ' ' + n['LCIA_unit'] +  ' (' + Math.round(n['ind_norm'] * 100) + '%)',
//                        + '\nInd: ' + Math.round(n['ind'] * 100)/100 + ' ' + n['LCIA_unit'] +  ' (' + Math.round(n['ind_norm'] * 100) + '%)'
//                        + '\nCum: ' + Math.round(n['cum'] * 100)/100 + ' ' + n['LCIA_unit'] +  ' (' + Math.round(n['cum_norm'] * 100) + '%)',
          product: n['product'],
          location: n['location'],
          id: n['id'],
          database: n['db'],
          class: n['class'],
          ind_norm: n['ind_norm'],
          tooltip: '<b>' + n['name'] + '</b>'
                    + '<br>Individual impact: &nbsp&nbsp&nbsp' + roundNumber(n['ind']) + ' ' + n['LCIA_unit'] +  ' (' + Math.round(n['ind_norm'] * 100) + '%)'
                    + '<br>Cumulative impact: ' + roundNumber(n['cum']) + ' ' + n['LCIA_unit'] +  ' (' + Math.round(n['cum_norm'] * 100) + '%)',
//          style: "fill: #f66; fill-opacity: 0.5",
        });
    });
    console.log("Nodes successfully loaded...");

    // edges --> graph
    data.edges.forEach(function(e) {
        var impact_or_benefit = "impact"
        if (e['impact'] < 0) {impact_or_benefit = "benefit"; console.log("BENEFIT");}

        graph.setEdge(e['source_id'], e['target_id'],
                {
                    label: wrapText(e['product']
                    + '\n(' + roundNumber(e['ind_norm']*100) + '%)', max_string_length),
//                    + '\n' + roundNumber(e['impact']) + ' ' + e['unit'] + ' (' + roundNumber(e['ind_norm'])*100 + '%)', max_string_length),
//                    labelStyle: "font-size: 2em; font-style: italic; text-decoration: underline;",
//                    labelStyle: "font-weight: bold;",
                    amount: e['amount'],
                    unit: e['unit'],
                    product: e['product'],
                    weight: Math.abs(e["impact"] / max_impact ) * max_edge_width,
                    tooltip: e['tooltip'],
//                    arrowhead: "vee",
                    class: impact_or_benefit,
                    curve: d3.curveBasis,
//                    style: "stroke: #f66; stroke-width: 3px; stroke-dasharray: 5, 5;",
                }
            );
    });
    console.log("Edges successfully loaded...")


    //re-renders canvas with updated dimensions of the screen
    canvas.render();
    //draws graph into canvas
	canvas.addItem();

	  // Adds click listener, calling handleMouseClick func
      var nodes = panCanvas.selectAll("g .node")
	      .on("click", handleMouseClick)
	      .on("mouseover", handleMouseOverNode)
	      .on("mouseout", function(d) {
//            d3.select(this).style("fill", "grey")
            div.transition()
                .duration(500)
                .style("opacity", 0);

        })
	      // this would change the node text color
//	      .style("fill", function(d) {
//	        console.log(color(graph.node(d).ind_norm))
//	        return color(graph.node(d).ind_norm);
//	      })

      // change node fill based on impact
	  var node_rects = panCanvas.selectAll("g .node rect")
	      .on("click", handleMouseClick)
	      .style("fill", function(d) {
    	      console.log(color(graph.node(d).ind_norm))
	      return color(graph.node(d).ind_norm);
	      })

      // listener for mouse-hovers
      var edges = panCanvas.selectAll("g .edgePath")
        .on("mouseover", handleMouseOverEdge)
        // set the stroke-width of edges according to data of the edge (e.g. flow value or impact)
//          .attr("stroke-width", function(d) { return Math.random()*10; })
        .attr("stroke-width", function(d) { return graph.edge(d).weight; })
//        .attr("viewBox", "0 0 50 50")
        .on("mouseout", function(d) {
//            d3.select(this).style("fill", "grey")
            div.transition()
                .duration(500)
                .style("opacity", 0);

        });

    // re-scale arrowheads to fit into edge (they become really big otherwise)
    markers = d3.selectAll("marker")
    		    .attr("viewBox", "0 0 60 60");  // basically zoom out on the arrowhead


    function handleMouseOverNode(n){
        console.log ("mouseover Node!")
//        d3.select(this).style("fill", "magenta")
        node = graph.node(n)

        div.transition()
            .duration(200)
            .style("opacity", .9);
        div	.html(node.tooltip)
//            .style("fill", )
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
    }

    function handleMouseOverEdge(e){
        console.log ("mouseover Edge!")
//        d3.select(this).style("fill", "magenta")
        edge = graph.edge(e)

        div.transition()
            .duration(200)
            .style("opacity", .9);
        div	.html(edge.tooltip)
//            .style("fill", )
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
    }

	// Function called on click
	function handleMouseClick(node){
        // make dictionary containing the node key and how the user clicked on it
        // see also mouse events: https://www.w3schools.com/jsref/obj_mouseevent.asp
        console.log("click on:", node)
        click_dict = {
            "database": graph.node(node).database,
             "id": graph.node(node).id
        }
        click_dict["mouse"] = event.button;
        click_dict["keyboard"] = {
            "shift": event.shiftKey,
            "alt": event.altKey,
        }
        console.log(click_dict)

        // pass click_dict (as json text) to python via bridge
        new QWebChannel(qt.webChannelTransport, function (channel) {
            window.bridge = channel.objects.bridge;
            window.bridge.node_clicked(JSON.stringify(click_dict));
            window.bridge.graph_ready.connect(update_graph);
        });
    };
};

// break strings into multiple lines after certain length if necessary
function wrapText(str, length) {
    //console.log(str.replace(/.{10}\S*\s+/g, "$&@").split(/\s+@/).join("\n"))
    return str.replace(/.{15}\S*\s+/g, "$&@").split(/\s+@/).join("\n")
//    return str.match(new RegExp('.{1,' + length + '}', 'g')).join("\n");
}

function roundNumber(number) {
//    return number.toFixed(2)
    return number.toPrecision(3)
//    return Math.round(number * 100)/100
}

new QWebChannel(qt.webChannelTransport, function (channel) {
    window.bridge = channel.objects.bridge;
    window.bridge.graph_ready.connect(update_graph);
});

