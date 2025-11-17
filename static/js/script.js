document.addEventListener("DOMContentLoaded", () => {

    // --- Analyser Page Logic ---
    const uploadBtn = document.getElementById('upload-btn');
    const predictBtn = document.getElementById('predict-btn');
    const manualForm = document.getElementById('manual-form');
    const uploadStatus = document.getElementById('upload-status');
    const resultsSection = document.getElementById('results-section');
    const resultText = document.getElementById('result-text');

    if (uploadBtn) {
        uploadBtn.addEventListener('click', handleReportUpload);
    }

    if (manualForm) {
        manualForm.addEventListener('submit', handlePrediction);
    }

    // --- Contact Page Logic ---
    const feedbackForm = document.getElementById('feedback-form');
    const feedbackStatus = document.getElementById('feedback-status');

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', handleFeedback);
    }

    /**
     * Handles the file upload for OCR extraction.
     */
    // script.js

async function handleReportUpload() {
    const fileInput = document.getElementById('report-file');
    const file = fileInput.files[0];
    const uploadBtn = document.getElementById('upload-btn'); // <-- NEW

    if (!file) {
        showStatus(uploadStatus, 'Please select a file first.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showStatus(uploadStatus, 'Uploading and processing... This may take a moment.', 'loading');
    
    // --- IMPROVEMENT ---
    uploadBtn.disabled = true; // <-- NEW (Disables the button)
    uploadBtn.textContent = 'Processing...'; // <-- NEW (Changes button text)

    try {
        const response = await fetch('/extract', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Failed to extract data.');
        }

        const data = await response.json();
        populateForm(data);
        showStatus(uploadStatus, 'Data extracted successfully! Please review the fields.', 'success');

    } catch (error) {
        showStatus(uploadStatus, error.message, 'error');
    } finally {
        // --- IMPROVEMENT ---
        // This 'finally' block runs no matter what (success or error)
        uploadBtn.disabled = false; // <-- NEW (Re-enables the button)
        uploadBtn.textContent = 'Upload and Extract Data'; // <-- NEW (Resets button text)
    }
}

    /**
     * Populates the manual form fields with data extracted from OCR.
     */
    function populateForm(data) {
        if (data.age) document.getElementById('age').value = data.age;
        if (data.height) document.getElementById('height').value = data.height;
        if (data.weight) document.getElementById('weight').value = data.weight;
        if (data.ap_hi) document.getElementById('ap_hi').value = data.ap_hi;
        if (data.ap_lo) document.getElementById('ap_lo').value = data.ap_lo;
        if (data.cholesterol) document.getElementById('cholesterol').value = data.cholesterol;
        if (data.glucose) document.getElementById('glucose').value = data.glucose;
        
        if (data.gender) {
            if (data.gender.toLowerCase() === 'male') {
                document.getElementById('gender').value = 'male';
            } else if (data.gender.toLowerCase() === 'female') {
                document.getElementById('gender').value = 'female';
            }
        }
    }

    /**
     * Handles the submission of the manual form for prediction.
     */
    async function handlePrediction(event) {
        event.preventDefault(); // Prevent default form submission
        showStatus(resultText, 'Analysing...', 'loading', resultsSection);

        // Collect all form data
        const formData = new FormData(manualForm);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || 'Prediction failed.');
            }

            const result = await response.json();
            displayResults(result);

        } catch (error) {
            showStatus(resultText, error.message, 'error', resultsSection);
        }
    }

    /**
     * Displays the prediction result in the results section.
     */
    function displayResults(result) {
        resultsSection.style.display = 'block';
        if (result.prediction === 1 && result.probability>75) {
            resultText.innerHTML = `
                <strong style="color: var(--danger-color);">High Risk</strong> 
                of Cardiovascular Disease
                <br>
                 
            `;
        } else if( result.prediction === 1 &&result.probability<75 &&result.probability>=60) {
            resultText.innerHTML = `
                <strong style="color: #FFB74D;">Moderate Risk</strong>

                of Cardiovascular Disease
                <br>
               
                
            `;
        } else {
            resultText.innerHTML = `
                <strong style="color: var(--success-color);">Low Risk</strong> 
                of Cardiovascular Disease
                <br>
                 
            `;
        }
    }


    /**
     * Handles submission of the feedback form.
     */
    async function handleFeedback(event) {
        event.preventDefault();
        
        const data = {
            name: document.getElementById('name').value,
            review: document.getElementById('review').value
        };

        if (!data.review) {
            showStatus(feedbackStatus, 'Please enter your feedback.', 'error');
            return;
        }

        showStatus(feedbackStatus, 'Submitting...', 'loading');

        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Failed to submit feedback.');

            await response.json();
            showStatus(feedbackStatus, 'Thank you for your feedback!', 'success');
            feedbackForm.reset(); // Clear the form

        } catch (error) {
            showStatus(feedbackStatus, error.message, 'error');
        }
    }

    /**
     * Helper function to show status messages to the user.
     */
    function showStatus(element, message, type, container = null) {
        element.textContent = message;
        element.className = `status-message status-${type}`;
        
        // If a container is passed (like resultsSection), show it.
        if (container) {
            container.style.display = 'block';
        }
    }
});