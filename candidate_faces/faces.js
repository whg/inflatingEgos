var terms = ['#snpmanifesto', '@nicolasturgeon', '#ukipmanifesto',
 '#conservativemanifesto', '#ukip', '@plaid_cymru', '@thegreenparty',
 '#votegreen', '@ukip', '#greenmanifesto', '#plaidmanifesto',
 '#cameronmustgo', '@natalieben', '#votelabour', '#labour', '#greens',
 '@thesnp', '#voteconservative', '#labourmanifesto', '#conservatives',
 '@uklabour', '#voteukip', '@conservatives', '@david_cameron',
 '@leannewood', '#votegreen2015', '#plaid15', '#voteplaid',
 '#greensurge', '#snp', '#teamcameron', '#changethetune',
 '#libdemmanifesto', '#libdems', '#votesnpgetsexy',
 '#forthecommongood', '#votesnp', '@nick_clegg', '@ed_milliband',
 '#believeinbritain', '#votelibdem', '#sexysocialism',
 '@nigel_farage', '@libdems'];

var MULT = 15;

$(document).ready(function() {

    var initialTweetOffset = $(".tweet").offset();
    var initialTweetSize = $(".tweet").css("font-size");
    
    $("img").each(function(i, e) {
        $(e).css({
            "height": "100px",
            "left": (i * 150) + "px",
        });
    });

    var n = 0;
    var imgwidth = 150;
    $(".img-container").each(function(i, e) {
        $(e).css({
            "left": (i * imgwidth) + "px",
        });
        n++;
    });
    $("#container").width(n * imgwidth);

    var w = $("body").width();
    if (w < n * imgwidth) {
        alert("Dude: make your browser bigger!");
    }

    $(document).keydown(function(e){
        console.log(e);
        var h = $("#farage").height();
        
    });


    function lineAndHighlightTweet() {

        var tweet = $(".tweet").text()
        
        var lastspace = 0;
        var ntweet = '';
        for (var i = 0; i < tweet.length; i++) {
            if (tweet[i] === ' ') {
                if (i - lastspace > 35) {
                    ntweet+= tweet.substring(lastspace, i) + ' <br/>';
                    lastspace = i;
                }
            }
        }

        ntweet+= tweet.substring(lastspace) + ' <br/>';

        // console.log(ntweet);
        var htweet = '';
        for (var i = 0; i < terms.length; i++) {
            var index = ntweet.toLowerCase().indexOf(terms[i]);
            if (index !== -1) {
                $(".tweet").html(ntweet.substring(0, index) + '<span class="term">' + terms[i] + '</span>' + ntweet.substring(index + terms[i].length));

                break;
            }
        }

    }

    function moveTweet(data) {
        var candidate = "#" + data.candidate.split(' ')[1].toLowerCase();
        
        var headoffset = $(candidate).offset();
        headoffset.left-= $(".tweet").width() / 2 + $(candidate).width() / 2;
        headoffset.top-= $(candidate).height() * 1.2;
        
        $(".tweet").css({ "position": "relative" });
        
        $(".tweet").animate({
            "top": headoffset.top,
            "left": headoffset.left,
            "font-size": 2,
        }, 1000, function() {

            $(".tweet").text("");

            var target = $(candidate).height();


            if (data.label === "POSITIVE") {
                target+= data.positive * data.confidence * MULT;
            }
            else if (data.label === "NEGATIVE") {
                target-= data.negative * data.confidence * MULT;
            }

            $(candidate).animate({
                'height': target
            });
            
            $(".tweet").offset(initialTweetOffset);
            $(".tweet").css({ "font-size": initialTweetSize });
        });
    }

    var counter = 0;
    var play = false;
    var data = null;
    
    $(document).keydown(function(e){

            moveTweet(data[counter-1]);

            setTimeout(function(){
                var d = data[counter];
                $(".tweet").text(d["tweet"]);

                lineAndHighlightTweet();
                delete d["tweet"];
                $("#meta").text(JSON.stringify(d));
                counter++;
            }, 1200);
            

            // if (counter < data.length) { 
            //     setTimeout(iter, 5000);
            // }

        
    });

    
    function loadData(d) {
        data = d;
        $("#tweets").html();
        (function iter() {
            // console.log(data[counter]);

            var d = data[counter];
            $(".tweet").text(d["tweet"]);

            lineAndHighlightTweet();
            delete d["tweet"];
            $("#meta").text(JSON.stringify(d));

            
            
            counter++;
            if (play && counter < data.length) {

                setTimeout(function(){
                    moveTweet(d);
                }, 3000);
                
                setTimeout(iter, 5000);
            }
        })();
    }


    // var c = 0;
    // setInterval(function() {
    //     $(".tweet").css({ "font-size": Math.sin(c * 0.01) * 10 + 15 });
    //     $(".tweet").parent().width(Math.sin(c * 0.01) * 100 + 200);
    //     c+= 1;
    // })
    
    $.getJSON('data.json', loadData);


});
