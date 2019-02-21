$('.new_note_form #id_message').each(function () {
    if ($(this).attr('parent_id') != undefined) {
        $(this).attr('placeholder', 'Add a note to the note...');
    } else {
        $(this).attr('placeholder', 'Add a note...');
    }
});

$('.reply-link').click(function () {
    $(`.new_note_form[note_id='${$(this).attr('note_id')}']`).toggleClass('hidden');
});