var loc = window.location;

var wsStart = "ws://";
if (loc.protocol == 'https:') {
    wsStart = "wss://";
}

$(".note").each(function () {
    var note = $(this);
    var note_container = note['0'];
    var note_id = note.attr('note_id');

    var endpoint = wsStart + loc.host + `/notes/resolve_note/${note_id}/`;
    var socket = new WebSocket(endpoint);

    socket.onmessage = function (e) {
        console.log("message", e);
        var responseData = JSON.parse(e.data);
        $(`.note[note_id='${responseData.note_id}']`).remove();
    }

    socket.onopen = function (e) {
        console.log("onopen", e);
        $(`.note[note_id=${note_id}] .resolve-note-link`).click(function (e) {
            console.log('shooould hvae disappeared');
            socket.send(note_id);
        });
    };

    socket.onerror = function (e) {
        console.log("onerror", e);
    };

    socket.onclose = function (e) {
        console.log("onclose", e);
    };

});