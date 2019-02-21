var loc = window.location;

var wsStart = "ws://";
if (loc.protocol == 'https:') {
    wsStart = "wss://";
}

$(".note").each(function () {
    var note_form = $(this);
    var note_container = note_form['0'];


    var endpoint = wsStart + loc.host + `/notes/edit_note/${note_form.attr('note_id')}/`;
    var socket = new WebSocket(endpoint);

    socket.onmessage = function (e) {
        console.log("message", e)
        var responseData = JSON.parse(e.data);
        if (responseData.editing_user != request_user_id) {
            $(`.note[note_id='${responseData.note_id}'] textarea`).val(responseData.note_message);
            console.log('updated the value');
        } else {
            console.log('didnt update the value');
        }
    }

    socket.onopen = function (e) {
        console.log("onopen", e);
        $(`textarea[name='message'][note_id='${note_form.attr('note_id')}']`).keyup(function () {
            var sendData = {
                'author': $(`input[name='author'][note_id='${note_form.attr('note_id')}']`).val(),
                'message': $(this).val(),
                'editing_user': request_user_id,
            };
            socket.send(JSON.stringify(sendData));
        });
    };

    socket.onerror = function (e) {
        console.log("onerror", e);
    };

    socket.onclose = function (e) {
        console.log("onclose", e);
    };

});