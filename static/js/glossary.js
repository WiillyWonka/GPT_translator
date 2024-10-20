async function addTerm() {
    const term = document.getElementById('term').value;
    const translation = document.getElementById('translation').value;
    const comment = document.getElementById('comment').value;

    if (term.trim() === '' || translation.trim() === '') return;

    const response = await fetch('/glossary/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ term, translation, comment })
    });

    if (response.ok) {
        loadGlossary();
    } else {
        alert('Failed to add term');
    }
}

async function deleteTerm() {
    const term = document.getElementById('delete-term').value;

    if (term.trim() === '') return;

    const response = await fetch('/glossary/', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ term })
    });

    if (response.ok) {
        loadGlossary();
    } else {
        alert('Failed to delete term');
    }
}

async function loadGlossary() {
    const response = await fetch('/glossary/');
    const data = await response.json();

    const glossaryList = document.getElementById('glossary-list');
    glossaryList.innerHTML = '';

    data.forEach(entry => {
        glossaryList.innerHTML += `<li>${entry.term} - ${entry.translation} (${entry.comment})</li>`;
    });
}

// Load glossary on page load
loadGlossary();