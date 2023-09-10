document.getElementById('predictForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const promptInput = document.getElementById('promptInput').value;
    const responseDiv = document.getElementById('responseText');
    
    // Clear previous response
    responseDiv.textContent = 'Loading...';
    
    try {
        const response = await fetch('http://neal-xps:8000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: promptInput,
            }),
        });

        const result = await response.json();
        responseDiv.textContent = result.predictions[0][0].generated_text;

    } catch (error) {
        responseDiv.textContent = 'Error occurred: ' + error.message;
    }
});
