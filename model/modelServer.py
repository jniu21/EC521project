from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

try:
    model = joblib.load("./random_forest_model.pkl")
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def predict_url(model, feature_dict):
    """
    Make predictions using the loaded Random Forest model.
    
    Args:
        model: Loaded joblib model
        feature_dict: Dictionary containing feature values
        
    Returns:
        Prediction from the model
    """
    required_features = [
        'having_IP_Address', 'URL_Length', 'Shortining_Service',
        'having_At_Symbol', 'double_slash_redirecting', 'Prefix_Suffix',
        'having_Sub_Domain', 'Domain_Registeration_Length', 'Favicon',
        'Port', 'HTTPS_token', 'Request_URL', 'Anchor_URL',
        'Links_in_Tags', 'Abnormal_URL', 'Domain_age', 'DNS_record',
        'Website_traffic', 'Page_rank', 'Google_Index'
    ]
    
    df = pd.DataFrame([feature_dict], columns=required_features)
    
    # Make prediction
    prediction = model.predict(df)
    return int(prediction[0])  # Convert numpy int to Python int for JSON serialization

def get_prediction_message(prediction):
    """
    Convert prediction value to corresponding message.
    """
    if prediction == -1:
        return 'phishing'
    elif prediction == 0:
        return 'malicious'
    elif prediction == 1:
        return 'legit'
    else:
        return 'unknown'

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded'
        }), 500

    try:
        # Get feature dictionary from request
        feature_dict = request.json
        
        # Make prediction
        prediction = predict_url(model, feature_dict)
        
        # Get corresponding message
        message = get_prediction_message(prediction)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)