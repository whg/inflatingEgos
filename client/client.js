var socket = null;
var isopen = false;
var candidate_data = null;

var NUMBER_LIMIT = 10;

function build_tweet(t) {
    return '<div class="tweet">' + t + '</div>'
}

function highlight_tags(tweet) {
    var ltweet = tweet.toLowerCase();

    // console.log(candidate_data.tags);
    var terms = candidate_data.tags;
    return tweet.parseHashtag().parseUsername();
}

function add_data_from_arg(t, arg) {
    t.find(".twitter-name b").text(arg["name"]);
    t.find(".twitter-user a").attr("href", "http://twitter.com/" + arg["handle"]);
    t.find(".twitter-handle").text("@" + arg["handle"]);
    t.find(".twitter-user img").attr("src", arg["user-img-url"]);
    t.find(".tweet-contents p").html(highlight_tags(arg["tweet"]));

    if (arg["retweeted-by"]) {
        t.find(".retweet-container span").text(arg["retweeted-by"] + " retweeted");
    }
    else {
        t.find(".retweet-container").remove();
    }
    
    function add_media(url) {
        if (url) {
            t.find(".tweet-img-container img").attr("src", url);
            // console.log("added img");
        }
        else {
            t.find(".tweet-img-container").remove();
        }
        
    }

    add_media(arg["media"]);
}

function insert_tweet(arg) {
    $("#main").prepend($("#twitter-template").html());

    var t = $("#main .twitter-container:first");

    add_data_from_arg(t, arg);
    

    t.css({ display: "none" });
    t.slideDown(500);
    // console.log("slide down");
    
    $("#main .twitter-container:gt(" + NUMBER_LIMIT + ")").remove();

    $("#main .twitter-container").each(function(i, e) {
        var v = i * 0.15;
        var r = candidate_data.colour.r;
        var g = candidate_data.colour.g;
        var b = candidate_data.colour.b;
        // var r = v, g = v, b = v;
        $(e).css({ "background": "rgba("+r+","+g+","+b+","+(1.0-v)+")" });
        $(e).find("div.container").css({ "background": "rgba("+r+","+g+","+b+","+(0.3-v*0.5)+")" });
    });
}

function favourites_and_retweets(arg) {
    $("#status").prepend($("#twitter-template").html());
    var t = $("#status .twitter-container:first");

    console.log("starting favs and rets with " + arg['tweet']);
    
    add_data_from_arg(t, arg);
    
    t.css( { opacity: 0, background: "white" });
    t.addClass("status");

    if (arg.retweets) {
        t.find(".status-container").toggleClass("hide");
        t.find(".status-container .retweets").text(arg.retweets);
        t.find(".status-container .favourites").text(arg.favourites);
    }
    else if (arg.amount) {
        t.find(".status-container").toggleClass("hide");
        t.find(".status-container .amount").text(arg.amount);
        t.find(".status-container .retweet-img").hide();
        t.find(".status-container .favourite-img").hide();
    }
    
    
    $("#main").animate({"opacity": 0 }, 2000, function() {
        $("#main").toggle(false);
        t.animate({"opacity": 1}, 2000, function() {
            t.css({ "position": "relative" });
            var that = this;
            setTimeout(function() {
                console.log(t);
                console.log("animating " );
                $(t).animate({ "top": -2000 }, 2000, function() {
                    $("#status").html("");
                    $("#main").toggle(true);
                    $("#main").animate({ "opacity": 1 }, 1000, function() {
                    });
                }); 
            }, 3000);
        });
    });
    
}

var main = {
    write: function (message, number) {
        var main = document.querySelector("#main");
        $("#main").prepend(build_tweet(message));
        $(".tweet:first").slideDown(500);
        $(".tweet:gt(5)").remove();
    },
    post: insert_tweet,
    personal_update: favourites_and_retweets,
    action_update: favourites_and_retweets
    
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
