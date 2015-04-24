 var socket = null;
 var isopen = false;

var main = {
    write: function (message, number) {
        var main = document.querySelector("#main");
        main.innerHTML+= "<p>" + message + "(" + number + ")";
    },
};

 window.onload = function() {
    socket = new WebSocket("ws://127.0.0.1:9000");
    socket.binaryType = "arraybuffer";
    socket.onopen = function() {
       console.log("Connected!");
       isopen = true;
    }
    socket.onmessage = function(e) {
       if (typeof e.data == "string") {
           var rpc = JSON.parse(e.data);
           main[rpc.func].apply(null, rpc.args);
           
          console.log("Text message received: " + e.data);
       }
    }
    socket.onclose = function(e) {
       console.log("Connection closed.");
       socket = null;
       isopen = false;
    }
 };

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
