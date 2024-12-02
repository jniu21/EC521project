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
        const features = await extractURLFeatures(url);
        res.json({ success: true, features });
    } catch (error) {
        console.error('Feature extraction error:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Feature extraction service running on port ${PORT}`);
});