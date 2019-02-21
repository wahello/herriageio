var loc = window.location;
var newNoteForm = $(".new_note_form");

var wsStart = "ws://";
if (loc.protocol == 'https:') {
    wsStart = "wss://";
}

$(newNoteForm).each(function () {
    newNoteForm = $(this);
    console.log('entered', $(this));

    var endpoint = wsStart + loc.host + `/notes/add_note/`;
    var socket = new WebSocket(endpoint);

    var newNoteAuthorInput = null;
    var newNoteMessageInput = null;

    socket.onmessage = function (e) {
        console.log('on message note', e)
        responseData = JSON.parse(e.data)
        console.log("BUILDING THE DOM");
        $(".notes-prepend").after(`                        
        <div class="col-md-4 note" note_id="${ responseData.note_id}">
            <div class="content">
                <textarea parent_id="${responseData.parent_id}" note_id="${ responseData.note_id}" name="message" cols="40" rows="10" value="${responseData.note_message}" class="textarea form-control" id="id_message" link="${responseData.edit_note_url}">${responseData.note_message}</textarea>

                <div class="action-container">
                    <a class="info-link" note_id="{{ note.id }}"><span class="info-note">🤔</span></a>  
                </div>

                <a link="${ responseData.resolve_note_url}" class="resolve-note-link" note_id="${responseData.note_id}"><span class="delete-note">👌</span></a>
                </p>
            </div>
        </div>`);
        $(".new-note-form-container #div_id_message textarea").val("");

        var new_note = $(`.note[note_id='${responseData.note_id}']`);
        var endpoint = wsStart + loc.host + `/notes/edit_note/${new_note.attr('note_id')}/`;
        var socket2 = new WebSocket(endpoint);

        socket2.onmessage = function (e) {
            console.log("message", e)
            var responseData = JSON.parse(e.data);
            $(`.note[note_id='${responseData.note_id}'] textarea`).val(responseData.note_message);
        }

        socket2.onopen = function (e) {
            console.log("onopen", e);

            $(`textarea[name='message'][parent_id='${responseData.note_id}']`).change(function () {
                parent_id = null;
                if ($(this).attr('parent_id') != null) {
                    console.log('parent id got for addition', $(this).attr('parent_id'));
                } else {
                    console.log('parent id got for addition', null)
                }

                var sendData = {
                    'author': request_user_id,
                    'message': $(this).val(),
                    'parent_id': parent_id,
                };
                socket.send(JSON.stringify(sendData));
            });
        };

        socket2.onerror = function (e) {
            console.log("onerror", e);
        };

        socket2.onclose = function (e) {
            console.log("onclose", e);
        };
    }

    socket.onopen = function (e) {
        console.log('opened', e);
        console.log('found this button', newNoteForm, newNoteForm.find("button[type='new_parent_note_button']"))
        newNoteForm.find("button[type='new_parent_note_button']").click(function (event) {
            event.preventDefault();

            console.log('entered the detection');

            if (newNoteForm.attr('parent_id') == null) {
                newNoteAuthorInput = newNoteForm.find("#id_author");
                newNoteMessageInput = newNoteForm.find("#id_message");
            } else {
                newNoteAuthorInput = $(`#new_note_form[parent_id='${newNoteForm.attr('parent_id')}' #id_author`);
                newNoteMessageInput = $(`#new_note_form[parent_id='${newNoteForm.attr('parent_id')}' #id_message`);
            }

            console.log(newNoteAuthorInput, newNoteMessageInput)

            if (newNoteMessageInput.val().length > 1) {
                console.log('too short');

                parent_id = null;
                if (newNoteForm.attr('parent_id') != null) {
                    console.log(newNoteForm.attr('parent_id'));
                } else {
                    console.log(null)
                }

                var sendData = {
                    'author': newNoteAuthorInput.val(),
                    'message': newNoteMessageInput.val(),
                    'parent_id': parent_id,
                }

                socket.send(JSON.stringify(sendData));

            }
        })
    }

    socket.onerror = function (e) {
        return;
    }
    socket.onclose = function (e) {
        return;
    }
});

$(document).ready(function () {
    $(".new-note-form-container #id_message").each(function () {
        parent_id = $(this).parent().parent().parent().parent().parent().attr('parent_id');
        if (parent_id != undefined) {
            $(this).attr('parent_id', parent_id);
        };
    });
});