async function addTrainSample() {
    const foreignText = document.getElementById('foreign-text').value;
    const translation = document.getElementById('translation').value;

    if (foreignText.trim() === '') {
        alert('Source text cannot be empty');
        return;
    }
    if (translation.trim() === '') {
        alert('Translation cannot be empty');
        return;
    }

    const response = await fetch('/train_samples/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ foreign_text: foreignText, translation: translation })
    });

    if (response.ok) {
        loadTrainSamples();
    } else if (response.status === 404) {
        alert('Train sample not found');
    } else {
        alert('Failed to add train sample');
    }
}

async function deleteTrainSample() {
    const sampleId = document.getElementById('sample-id').value;

    if (sampleId.trim() === '') {
        alert('Sample ID cannot be empty');
        return;
    }

    const response = await fetch(`/train_samples/${sampleId}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        loadTrainSamples();
        document.getElementById('train-sample-details').innerHTML = '';
    } else if (response.status === 404) {
        alert('Train sample not found');
    } else {
        alert('Failed to delete train sample');
    }
}

async function viewTrainSample() {
    const sampleId = document.getElementById('sample-id').value;

    if (sampleId.trim() === '') {
        alert('Sample ID cannot be empty');
        return;
    }

    const response = await fetch(`/train_samples/${sampleId}`);
    const data = await response.json();

    if (response.ok) {
        const detailsDiv = document.getElementById('train-sample-details');
        detailsDiv.innerHTML = `
            <p><strong>ID:</strong> ${data.id}</p>
            <p><strong>Foreign Text:</strong> ${data.foreign_text}</p>
            <p><strong>Translation:</strong> ${data.translation}</p>
        `;
    } else if (response.status === 404) {
        alert('Train sample not found');
    } else {
        alert('Failed to view train sample');
    }
}

async function loadTrainSamples() {
    const response = await fetch('/train_samples/');
    const data = await response.json();

    const trainSamplesList = document.getElementById('train-samples-list');
    trainSamplesList.innerHTML = '';

    data.forEach(sample => {
        trainSamplesList.innerHTML += `<li>${sample.id}</li>`;
    });
}

// New Function for Finetuning
async function uploadDataset() {
    const response = await fetch('train_samples/upload', {
        method: 'POST'
    });

    const data = await response.json();

    if (response.ok) {
        alert(`Success: ${data.message}`);
    } else {
        alert(`Failed to uploading dataset: ${data.message}`);
    }
}

// Load train samples on page load
loadTrainSamples();
