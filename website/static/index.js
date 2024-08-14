function deleteNote(noteId) {
    fetch(`/delete_note/${noteId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('note-' + noteId).remove();
        } else {
            alert('Failed to delete the note.');
        }
    });
}