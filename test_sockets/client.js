 var socket = null;
 var isopen = false;

var PORTS = {
    "cameron": 9001,
    "clegg": 9002,
    "miliband": 9003,
    "sturgeon": 9004,
    "wood": 9005,
    "bennett": 9006,
    "farage": 9007
};

function build_tweet(t) {
    return '<div class="tweet">' + t + '</div>'
}

var main = {
    write: function (message, number) {
        var main = document.querySelector("#main");
        $("#main").prepend(build_tweet(message));
        $(".tweet:first").slideDown(500);
        $(".tweet:gt(5)").remove();
    },
};

function openSocket(port) {
    socket = new WebSocket("ws://127.0.0.1:" + port);
    socket.binaryType = "arraybuffer";
    socket.onopen = function() {
       console.log("Connected!");
       isopen = true;
    }
    socket.onmessage = function(e) {
       if (typeof e.data == "string") {
           try {
               var rpc = JSON.parse(e.data);
               main[rpc.func].apply(null, rpc.args);
           } catch(e) {
               console.log("not json");
           }
           
          console.log("Text message received: " + e.data);
       }
       else console.log("not string");
    }
    socket.onclose = function(e) {
       console.log("Connection closed.");
       socket = null;
       isopen = false;
    }
}

$(document).ready(function() {
    var candidate = location.hash.substr(1);
    if (candidate.length < 3) {
        var ts = location.href.split('/');
        var filebasename = ts[ts.length-1].split('.')[0];
        if (filebasename) {
            candidate = filebasename;
        }
        else {
            alert("no candidate");
        }
    }

    var port = PORTS[candidate];
    console.log('opening on port ' + port);
    openSocket(port);
});

function sendText() {
    if (isopen) {
       socket.send("Hello, world!");
       console.log("Text message sent.");               
    } else {
       console.log("Connection not opened.");
    }
}

function sendBinary() {
    if (isopen) {
       var buf = new ArrayBuffer(32);
       var arr = new Uint8Array(buf);
       for (i = 0; i < arr.length; ++i) arr[i] = i;
       socket.send(buf);
       console.log("Binary message sent.");
    } else {
       console.log("Connection not opened.");
    }
}
