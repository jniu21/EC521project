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
    const showAnalysisResult = (result, type) => {
        analysisResult.textContent = result;
        analysisResult.className = `message-box ${type}`;
        analysisResult.style.display = 'block';
    };

    // Function to analyze URL
    const analyzeCurrentUrl = async (url, htmlContent) => {
        try {
            showMessage('Analyzing URL...', 'info');
            
            const response = await chrome.runtime.sendMessage({
                action: "analyzeUrl",
                url: url,
                htmlContent: htmlContent
            });

            if (response.success) {
                const resultType = response.message === 'legit' ? 'success' : 'error';
                const resultMessage = `Analysis Result: This URL appears to be ${response.message}`;
                showAnalysisResult(resultMessage, resultType);
                showMessage('Analysis complete', 'success');
            } else {
                showAnalysisResult('Unable to analyze URL', 'error');
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
                const [{ result: htmlContent }] = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    function: () => document.documentElement.outerHTML
                });
                await analyzeCurrentUrl(tab.url, htmlContent);
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
                    const [{ result: htmlContent }] = await chrome.scripting.executeScript({
                        target: { tabId: tab.id },
                        function: () => document.documentElement.outerHTML
                    });
                    await analyzeCurrentUrl(tab.url, htmlContent);
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