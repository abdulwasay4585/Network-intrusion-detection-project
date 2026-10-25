document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prediction-form');
    const predictBtn = document.getElementById('predict-btn');
    const btnText = predictBtn.querySelector('.btn-text');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const predictionValue = document.getElementById('prediction-value');

    const API_URL = 'http://localhost:8000/predict';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Feedback
        btnText.style.display = 'none';
        loader.style.display = 'block';
        predictBtn.disabled = true;
        resultContainer.classList.add('hidden');

        const formData = new FormData(form);
        const data = {
            hour: parseInt(formData.get('hour')),
            day_of_week: parseInt(formData.get('day_of_week')),
            is_weekend: parseInt(formData.get('is_weekend')),
            lag_1: parseFloat(formData.get('lag_1')),
            lag_2: parseFloat(formData.get('lag_2')),
            rolling_3: parseFloat(formData.get('rolling_3'))
        };

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                throw new Error('Prediction failed. Is the backend running?');
            }

            const result = await response.json();
            
            // Show result with animation
            predictionValue.textContent = result.predicted_dropped_packets.toFixed(2);
            resultContainer.classList.remove('hidden');
            
            // Scroll to result
            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
        } finally {
            // Restore UI
            btnText.style.display = 'block';
            loader.style.display = 'none';
            predictBtn.disabled = false;
        }
    });

    // Add some subtle parallax or mouse follow effect if desired
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        
        document.querySelector('.blob-1').style.transform = `translate(${x * 50}px, ${y * 50}px)`;
        document.querySelector('.blob-2').style.transform = `translate(${x * -30}px, ${y * -30}px)`;
    });
});
