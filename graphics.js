/**
 * Created by marek on 30.04.2017.
 * Based on mesa/examples/Flockers/flockers/simple_continuous_canvas.js
 */

var AgentVisualization = function (width, height, context) {
    this.draw = function (objects) {
        for (var i = 0; i < objects.length; i++) {
            var p = objects[i];
            this.drawCircle(p.x, p.y, p.r, p.Color)
        }
    };
    
    this.drawCircle = function (x, y, radius, color) {
        var cx = x * width;
        var cy = y * height;
        var r = radius;

        context.beginPath();
        context.arc(cx, cy, r, 0, Math.PI * 2, false);
        context.closePath();
        
        context.strokeStyle = context.fillStyle = color;
        context.stroke();
        context.fill();
    };

    this.resetCanvas = function () {
        context.clearRect(0, 0, height, width);
        context.beginPath();
    }
};

var VerySimpleContinuousModule = function (canvas_width, canvas_height) {
    var canvas_tag =
        "<canvas width='" + canvas_width + "' height='" + canvas_height + "' style='border:1px dotted'></canvas>";
    var canvas = $(canvas_tag)[0];
    $("body").append(canvas);

    var context = canvas.getContext("2d");
    var canvasDraw = new AgentVisualization(canvas_width, canvas_height, context);

    this.render = function (data) {
        canvasDraw.resetCanvas();
        canvasDraw.draw(data);
    };

    this.reset = function () {
        canvasDraw.resetCanvas();
    };
};
