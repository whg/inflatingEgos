var socket = null;
var isopen = false;
var candidate_data = null;

function build_tweet(t) {
    return '<div class="tweet">' + t + '</div>'
}

function highlight_tags(tweet) {
    var ltweet = tweet.toLowerCase();

    console.log(candidate_data.tags);
    var terms = candidate_data.tags;
    return tweet.parseHashtag().parseUsername();
}

function insert_tweet(arg) {
    $("#main").prepend($("#twitter-template").html());

    var t = $("#main .twitter-container:first");

    t.find(".twitter-name b").text(arg["name"]);
    t.find(".twitter-user a").attr("href", "http://twitter.com/" + arg["handle"]);
    t.find(".twitter-handle").text("@" + arg["handle"]);
    t.find(".twitter-user img").attr("src", arg["user-img-url"]);
    t.find(".tweet-contents p").html(highlight_tags(arg["tweet"]));

    function add_media(url) {
        if (url) {
            t.find(".tweet-img-container img").attr("src", url);
        }
        else {
            t.find(".tweet-img-container").remove();
        }
        
    }

    add_media(arg["url"]);

    t.css({ display: "none" });
    t.slideDown(500);
    // console.log("slide down");
    
    $(".twitter-container:gt(5)").remove();
}

var main = {
    write: function (message, number) {
        var main = document.querySelector("#main");
        $("#main").prepend(build_tweet(message));
        $(".tweet:first").slideDown(500);
        $(".tweet:gt(5)").remove();
    },
    post: insert_tweet,
    
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
           // try {
               var rpc = JSON.parse(e.data);
               main[rpc.func].call(null, rpc.arg);
           // } catch(e) {
               // console.log("not json");
           // } 
           
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

// $(document).ready(function() {
$.getJSON('../info.json', function(infos) {

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
    
    candidate_data = infos[candidate];
    
    var port = infos[candidate]['ws_port'];
    console.log('opening on port ' + port);
    openSocket(port);



    // $("#main").prepend($("#twitter-template").html());

    // var t = $("#main .twitter-container:first");
    // console.log(t);
    // t.find(".twitter-name b").text("David Cameron");
    // t.find(".twitter-handle").text("@David_Cameron");
    // t.find(".twitter-user img").attr("src", "https://pbs.twimg.com/profile_images/567663852796399617/mYltRqyb_normal.jpeg");
    // t.find(".tweet-contents p").text("This is a tweet");
    // t.find(".tweet-img-container img").attr("src", "https://pbs.twimg.com/media/CDlILU9W0AAFB0O.png:large");
    
    
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
