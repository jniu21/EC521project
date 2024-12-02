async function analyzeUrl(url, htmlContent) {
    try {
        // Get features from feature extraction service
        const featureResponse = await fetch('http://localhost:3000/extract-features', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        const featureResult = await featureResponse.json();
        if (!featureResult.success) {
            throw new Error(featureResult.error);
        }

        // Send features to model server
        const modelResponse = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(featureResult.features)
        });
        
        const result = await modelResponse.json();
        return result;
    } catch (error) {
        console.error("Error in URL analysis:", error);
        return { 
            success: false, 
            message: "Failed to analyze URL: " + error.message 
        };
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyzeUrl") {
        analyzeUrl(request.url, request.htmlContent)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ 
                success: false, 
                message: error.toString() 
            }));
        return true;
    }
});