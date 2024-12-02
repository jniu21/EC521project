require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { extractURLFeatures } = require('./feature_extraction');

const app = express();
app.use(cors());
app.use(express.json());

// Endpoint to handle feature extraction
app.post('/extract-features', async (req, res) => {
    try {
        const { url } = req.body;
        console.log('Received request for URL:', url);
        
        const start = Date.now();
        const features = await extractURLFeatures(url);
        const timeElapsed = Date.now() - start;
        
        console.log(`Feature extraction completed in ${timeElapsed}ms`);
        
        // Check if features were actually returned
        if (!features) {
            throw new Error('No features returned');
        }
        
        res.json({ 
            success: true, 
            features,
            extractionTime: timeElapsed 
        });
    } catch (error) {
        console.error('Feature extraction error:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message || 'Feature extraction failed'
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Feature extraction service running on port ${PORT}`);
});