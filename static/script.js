document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('outfitForm');
    const optionsSection = document.getElementById('optionsSection');
    const outfitOptions = document.getElementById('outfitOptions');
    const selectedOutfit = document.getElementById('selectedOutfit');
    const outfitDescription = document.getElementById('outfitDescription');
    const outfitImage = document.getElementById('outfitImage');

    // Replace this with your Flask backend URL
    const FLASK_BACKEND = 'http://localhost:5000';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const occasion = document.getElementById('occasion').value;

        try {
            const response = await fetch(`${FLASK_BACKEND}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `question=${encodeURIComponent(occasion)}`
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');

            // Extract options from the response
            const options = Array.from(doc.querySelectorAll('button[name="choice"]'))
                .map(button => button.value);

            // Display options
            displayOptions(options);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to get outfit suggestions. Please try again.');
        }
    });

    function displayOptions(options) {
        outfitOptions.innerHTML = '';
        options.forEach((option, index) => {
            const button = document.createElement('button');
            button.className = 'outfit-option';
            button.textContent = `${index + 1}. ${option}`;
            button.addEventListener('click', () => selectOutfit(option));
            outfitOptions.appendChild(button);
        });
        optionsSection.classList.remove('hidden');
        selectedOutfit.classList.add('hidden');
    }

    async function selectOutfit(option) {
        try {
            const response = await fetch(`${FLASK_BACKEND}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `choice=${encodeURIComponent(option)}&options_str=${encodeURIComponent(option)}`
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');

            // Update the selected outfit display
            outfitDescription.textContent = option;
            outfitImage.src = `${FLASK_BACKEND}/static/result.png?t=${new Date().getTime()}`; // Add timestamp to prevent caching
            selectedOutfit.classList.remove('hidden');
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate outfit image. Please try again.');
        }
    }
}); 