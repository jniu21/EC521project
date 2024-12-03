document.addEventListener('DOMContentLoaded', async () => {
    const toggle = document.getElementById('toggleSwitch');
    const status = document.getElementById('status');
    const urlDisplay = document.getElementById('currentUrl');
    const messageContainer = document.getElementById('messageContainer');
    const analysisResult = document.getElementById('analysisResult');

    // Function to update message
    const showMessage = (message, type = 'info') => {
        messageContainer.textContent = message;
        messageContainer.className = `message-box ${type}`;
        messageContainer.style.display = 'block';
    };

    // Function to show analysis result
    const showAnalysisResult = (features, extractionTime) => {
        // Create a formatted display of all features
        const featureList = Object.entries(features)
            .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
            .join('<br>');

        analysisResult.innerHTML = `
            <h3>Feature Extraction Results:</h3>
            <div>Extraction Time: ${extractionTime}ms</div>
            <div class="feature-list">
                ${featureList}
            </div>
        `;
        analysisResult.className = 'message-box info';
        analysisResult.style.display = 'block';
    };

    // Function to analyze URL
    const analyzeCurrentUrl = async (url) => {
        try {
            showMessage('Analyzing URL...', 'info');
            
            const response = await chrome.runtime.sendMessage({
                action: "analyzeUrl",
                url: url
            });

            if (response.success) {
                showAnalysisResult(response.features, response.extractionTime);
                showMessage('Analysis complete', 'success');
            } else {
                analysisResult.textContent = 'Unable to analyze URL';
                analysisResult.className = 'message-box error';
                analysisResult.style.display = 'block';
                showMessage(response.message, 'error');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            showMessage('Failed to analyze URL', 'error');
        }
    };

    // Get initial toggle state
    const { isEnabled } = await chrome.storage.local.get('isEnabled');
    toggle.checked = isEnabled;
    status.textContent = isEnabled ? 'Protection is On' : 'Protection is Off';

    // Get and display current URL immediately
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab?.url) {
            urlDisplay.textContent = tab.url;
            
            if (tab.url.startsWith('chrome://') || 
                tab.url.startsWith('chrome-extension://') || 
                tab.url.startsWith('edge://')) {
                showMessage('This is a restricted page that cannot be analyzed', 'error');
                toggle.disabled = true;
            } else if (isEnabled) {
                await analyzeCurrentUrl(tab.url);
            }
        }
    } catch (error) {
        urlDisplay.textContent = 'Unable to detect URL';
        showMessage('Error accessing page content', 'error');
    }

    // Handle toggle change
    toggle.addEventListener('change', async () => {
        const isEnabled = toggle.checked;
        await chrome.storage.local.set({ isEnabled });

        if (isEnabled) {
            try {
                const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                if (tab?.url) {
                    await analyzeCurrentUrl(tab.url);
                }
                status.textContent = 'Protection is On';
            } catch (error) {
                console.error('Error:', error);
                showMessage(error.message, 'error');
                toggle.checked = false;
                await chrome.storage.local.set({ isEnabled: false });
                status.textContent = 'Protection is Off';
            }
        } else {
            status.textContent = 'Protection is Off';
            messageContainer.style.display = 'none';
            analysisResult.style.display = 'none';
        }
    });
});