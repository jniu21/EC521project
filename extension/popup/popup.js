document.addEventListener('DOMContentLoaded', async () => {
    const toggle = document.getElementById('toggleSwitch');
    const status = document.getElementById('status');

    const { isEnabled } = await chrome.storage.local.get('isEnabled');
    toggle.checked = isEnabled;
    status.textContent = isEnabled ? 'Protection is On' : 'Protection is Off';

    toggle.addEventListener('change', async () => {
        const isEnabled = toggle.checked;
        await chrome.storage.local.set({ isEnabeld });
        status.textContent = isEnabled ? 'Protection is On' : 'Protection is Off';

        chrome.runtime.sendMessage({type: 'TOGGLE_PROTECTION', isEnabled});
    });
});