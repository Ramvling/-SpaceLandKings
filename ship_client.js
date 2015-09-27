// This is where we define our messages (similar to an enum)
var MSG_LOGIN = 1;
var MOVE_INPUT = 2;
var TURN = 3;
var SCORE = 4;
var HEALTH = 5;
var GAMEOVER = 7;

var INCOMING = false;
var OUTGOING = true;
var player = {position:[0,0,0],moves:10, health:100,isDead:false,regen:5, missles:3, bombs:3, score:0};
var turn = true;
var commandString = ""

function handleMovement(dirr) {
    if (player.moves > 0) {
        commandString += dirr + " ";
       player.moves -= 1;
        $("#commands").text(commandString);
        $("#moves").text(player.moves);
    }
}
function handleFire() {
    if (player.moves > 0) {
        commandString += "Fire ";
       player.moves -= 1;
        $("#commands").text(commandString);
        $("#moves").text(player.moves);
    }
}

$(document).ready(function() {
   // Setup our message objects (packets)
    setupMessages();
    $("#game").hide();

    $("#login").click(function() {
        startConnection();
        
    });

    $("#end_turn").click(function() {
        handleTurnOver();
    });

    $("#up").click(function() {
       handleMovement("Up"); 
    });

     $("#down").click(function() {
       handleMovement("Down"); 
    });


    $("#left").click(function() {
      handleMovement("Left");  
    });

    $("#right").click(function() {
        handleMovement("Right");
    });

    $("#forward").click(function() {
        handleMovement("Forward");
    });

    $("#backward").click(function() {
        handleMovement("Backward");
    });

    $("#fire").click(function() {
        handleFire();
    });

    // This interval can be used for anything, but it currently only handles incoming messaged.
    setInterval(gameLoop, 15);
});

function setupMessages() {
    // Incoming MSG_LOGIN
    var m1 = createMsgStruct(MSG_LOGIN, false);
    // This packet will be carrying two chars
    m1.addChars(2);

    // Outgoing MSG_LOGIN
    var i1 = createMsgStruct(MSG_LOGIN, true);
    // This packet sends a string (our name) to the server
    i1.addString();

    //Test message
    var move  = createMsgStruct(MOVE_INPUT, OUTGOING);
    move.addString();

    var turn = createMsgStruct(TURN, INCOMING);
   turn.addChars(1);

    var done = createMsgStruct(TURN, OUTGOING);
    done.addChars(1);

    var score = createMsgStruct(SCORE, INCOMING);
    score.addString();

    var gameOver = createMsgStruct(GAMEOVER, INCOMING);
    gameOver.addString();

    var health = createMsgStruct(HEALTH, INCOMING);
    health.addString();
}

function startConnection() {
    // This will be called when the connection is successful 
    var onopen = function() {
        // We ask for a new packet for type MSG_LOGIN
        var packet = newPacket(MSG_LOGIN);
        // Writing our name. 'Write' is currently expecting a String,
        // as that is what we defined earlier.
        packet.write($("#name").val());
        // and then we send the packet!
        packet.send();
        $("#notify").text("Connected!");
        $("#login").hide();
        $("#name").hide();
        $('#gameOver').hide();
        //just hiding for now, probably needs better show/hide logic. 
        $("#notify").hide();
        $("#game").show();
        $("#title").hide();
    }

    // This will be called when the connection is closed
    var onclose = function() {
        window.location.href = '/';
    }

    // Start the connection!
    //wsconnect("ws://128.61.70.189:8886", onopen, onclose);
    wsconnect("ws://localhost:8886", onopen, onclose);
}

function handleGameOver(msg) {
    $("#game").hide();
    $("#gameOver").show();
    $("#gameOverMsg").text(msg);
}

function handleTurnStart(){
    if (!player.isDead) {
         $("#button_console").show();
         $("#end_turn").show();
         $("#message").text("It's your turn!");
        turn = true;
        console.log("turn handled");   
        $("#moves").text(player.moves);
    }
}

function handleTurnOver(){
         $("#button_console").hide();
         $("#end_turn").hide();
         $("#message").text("'Waiting on other players");
        turn = false;
        console.log("turn over");   
         var packet = newPacket(MOVE_INPUT);
        packet.write(commandString); 
        commandString = "";
        packet.send();
        $("#moves").text(player.moves);
        $("#commands").text(commandString);

        player.moves += player.regen;

        //note, when we do the whole big string thing at the end, this kind of message can be deleted
       // var packet = newPacket(TURN);
      //  packet.write('o'); 
       // packet.send();
}
// This function handles incoming packets
function handleNetwork() {
    // First we check if we have enough data
    // to handle a full packet
    if (!canHandleMsg()) {
        return;
    }

    // Read the packet in
    var packet = readPacket();

    // Find out what type of packet it is
    msgID = packet.msgID;

    // And handle it!
    if (msgID === MSG_LOGIN) {
        var pid = packet.read();
        alert("You are client number " + pid);
    }

    if (msgID == MOVE_INPUT) {
        console.log(packet.read());
    }

    if (msgID == TURN) {
        console.log("turn start");
        handleTurnStart();
    }

    if (msgID == SCORE) {
        var msg = packet.read().split(" ");
        player.score = msg[0];
        $("#score").text(player.score);
        $("#position").text(msg[1]);
    }

    if (msgID == HEALTH) {
        var msg = packet.read();
        player.health = parseInt(msg)
        $("#health").text(player.health);
    }

    if (msgID == GAMEOVER) {
        handleGameOver(packet.read());
    }
}

//sync player with server?


// This is called every 15 millis, and is currently used to
// handle incoming messaged. This can do more.
function gameLoop() {
    handleNetwork();
   if (player.moves <= 0) {
        handleTurnOver();
    } 
}

// Does a simple httpGet request. Not used in this example.
function httpGet(url, callback, carryout) {
	var xmlHttp = new XMLHttpRequest();
	xmlHttp.open("GET", url, true);
	xmlHttp.onreadystatechange = function() {
		if (xmlHttp.readyState == 4) {
			if (xmlHttp.status == 200) {
				alert(xmlHttp.responseText);
			}
		}
	}
	xmlHttp.send();
}
