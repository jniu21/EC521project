const axios = require('axios');

async function testFeatureExtraction() {
    const testUrl = 'https://www.google.com';
    
    try {
        console.log('Testing feature extraction service...');
        console.log(`Sending request for URL: ${testUrl}\n`);
        
        const response = await axios.post('http://localhost:3000/extract-features', {
            url: testUrl
        }, {
            timeout: 30000 // 30 second timeout since feature extraction can take time
        });
        
        if (response.data.success) {
            console.log('✓ Test successful');
            console.log('\nExtracted Features:');
            console.log(JSON.stringify(response.data.features, null, 2));
            console.log(`\nExtraction Time: ${response.data.extractionTime}ms`);
        } else {
            console.log('✗ Test failed');
            console.log('Error:', response.data.error);
        }
    } catch (error) {
        console.error('Error during test:');
        if (error.response) {
            console.error('Server responded with:', error.response.data);
        } else if (error.request) {
            console.error('No response received. Is the server running?');
        } else {
            console.error('Error:', error.message);
        }
    }
}

testFeatureExtraction();