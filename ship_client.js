// This is where we define our messages (similar to an enum)
var MSG_LOGIN = 1;
var MOVE_INPUT = 2;
var INCOMING = false;
var OUTGOING = true;

$(document).ready(function() {
   // Setup our message objects (packets)
    setupMessages();
    $("#game").hide();

    $("#login").click(function() {
        startConnection();
        
    });

    $("#up").click(function() {
        var packet = newPacket(MOVE_INPUT);
        packet.write("Up");
        packet.send();
    });

     $("#down").click(function() {
        var packet = newPacket(MOVE_INPUT);
        packet.write("Down");
        packet.send();
    });


    $("#left").click(function() {
        var packet = newPacket(MOVE_INPUT);
        packet.write("Left");
        packet.send();
    });

    $("#right").click(function() {
        var packet = newPacket(MOVE_INPUT);
        packet.write("Right");
        packet.send();
    });

    $("#forward").click(function() {
        var packet = newPacket(MOVE_INPUT);
        packet.write("Forward");
        packet.send();
    });

    $("#backward").click(function() {
        var packet = newPacket(MOVE_INPUT);
        packet.write("Backward");
        packet.send();
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

    var testIn = createMsgStruct(MOVE_INPUT, false);
    testIn.addString();
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
    wsconnect("ws://localhost:8886", onopen, onclose);
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
}

// This is called every 15 millis, and is currently used to
// handle incoming messaged. This can do more.
function gameLoop() {
    handleNetwork();
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
