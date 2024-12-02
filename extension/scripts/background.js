async function analyzeUrl(url) {
    try {
        console.log('Sending URL to feature extraction service:', url);
        
        // Get features from Node.js server
        const featureResponse = await fetch('http://localhost:3000/extract-features', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        if (!featureResponse.ok) {
            throw new Error(`Feature extraction failed: ${featureResponse.statusText}`);
        }
        
        const featureResult = await featureResponse.json();
        console.log('Features received:', featureResult);
        
        return {
            success: true,
            features: featureResult.features,
            extractionTime: featureResult.extractionTime
        };
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
        console.log('Received analysis request for URL:', request.url);
        analyzeUrl(request.url)
            .then(result => {
                console.log('Analysis result:', result);
                sendResponse(result);
            })
            .catch(error => {
                console.error('Analysis error:', error);
                sendResponse({ 
                    success: false, 
                    message: error.toString() 
                });
            });
        return true;
    }
});