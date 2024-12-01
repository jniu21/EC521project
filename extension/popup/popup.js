document.addEventListener('DOMContentLoaded', async () => {
    const toggle = document.getElementById('toggleSwitch');
    const status = document.getElementById('status');
    const urlDisplay = document.getElementById('currentUrl');
    const messageContainer = document.getElementById('messageContainer');

    // Function to update message
    const showMessage = (message, type = 'info') => {
        messageContainer.textContent = message;
        messageContainer.className = `message-box ${type}`;
        messageContainer.style.display = 'block';
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
            } else {
                // Get HTML content immediately and show message
                const [{ result: htmlContent }] = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    function: () => document.documentElement.outerHTML
                });
                showMessage('Successfully retrieved HTML content from the current page', 'success');
            }
        }
    } catch (error) {
        urlDisplay.textContent = 'Unable to detect URL';
        showMessage('Error accessing page content', 'error');
    }

    // Get current tab URL and HTML
    const getCurrentPageInfo = async () => {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const url = tab.url;

        if (url.startsWith('chrome://') || 
            url.startsWith('chrome-extension://') || 
            url.startsWith('edge://')) {
            throw new Error('This page cannot be analyzed (restricted URL)');
        }

        const [{ result: htmlContent }] = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: () => document.documentElement.outerHTML
        });

        showMessage('Successfully retrieved new HTML content', 'success');
        return { url, htmlContent };
    };

    // Handle toggle change
    toggle.addEventListener('change', async () => {
        const isEnabled = toggle.checked;
        await chrome.storage.local.set({ isEnabled });

        if (isEnabled) {
            try {
                showMessage('Analyzing page...', 'info');
                const { url, htmlContent } = await getCurrentPageInfo();
                
                // Send message to background script
                chrome.runtime.sendMessage({
                    type: 'TOGGLE_PROTECTION',
                    isEnabled,
                    data: {
                        url: url,
                        html: htmlContent
                    }
                });

                status.textContent = 'Protection is On';
                urlDisplay.textContent = url;
                showMessage('HTML content retrieved', 'success');
            } catch (error) {
                console.error('Error getting page info:', error);
                showMessage(error.message, 'error');
                toggle.checked = false;
                await chrome.storage.local.set({ isEnabled: false });
                status.textContent = 'Protection is Off';
            }
        } else {
            status.textContent = 'Protection is Off';
            messageContainer.style.display = 'none';
            chrome.runtime.sendMessage({
                type: 'TOGGLE_PROTECTION',
                isEnabled
            });
        }
    });
});