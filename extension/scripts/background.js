async function analyzeUrl(url) {
    try {
        // Step 1: Feature extraction from Node.js server
        const featureResponse = await fetch('http://localhost:3000/extract-features', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        const featureResult = await featureResponse.json();
        if (!featureResult.success) {
            throw new Error(featureResult.error);
        }

        // Step 2: Send features to Python model server
        const modelResponse = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(featureResult.features)
        });

        const modelResult = await modelResponse.json();
        
        return {
            success: true,
            features: featureResult.features,
            prediction: modelResult.message,
            extractionTime: featureResult.extractionTime
        };
    } catch (error) {
        console.error("Error:", error);
        return { success: false, message: error.message };
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyzeUrl") {
        analyzeUrl(request.url)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, message: error.toString() }));
        return true;
    }
});