from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import json

app = Flask(__name__)
CORS(app)

try:
    model = joblib.load("./random_forest_model_2.pkl")
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def predict_url(model, feature_dict):
    required_features = [
        'having_IP_Address', 'URL_Length', 'Shortining_Service',
        'having_At_Symbol', 'double_slash_redirecting', 'Prefix_Suffix',
        'having_Sub_Domain', 'Domain_Registeration_Length', 'Favicon',
        'Port', 'HTTPS_token', 'Request_URL', 'Anchor_URL',
        'Links_in_Tags', 'Abnormal_URL', 'Domain_age', 'DNS_record',
        'Page_rank', 'Google_Index'
    ]
    
    # print("\n=== Feature Dictionary ===")
    # print(json.dumps(feature_dict, indent=2))
    # print("======================\n")
    
    df = pd.DataFrame([feature_dict], columns=required_features)
    
    # print("=== DataFrame ===")
    # print(df)
    # print("===============\n")
    
    prediction = model.predict(df)
    return int(prediction[0])

def get_prediction_message(prediction):
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
        print("\n=== Received Request ===")
        print("Content-Type:", request.headers.get('Content-Type'))
        print("Request Data:", json.dumps(request.json, indent=2))
        print("=====================\n")
        
        feature_dict = request.json
        prediction = predict_url(model, feature_dict)
        message = get_prediction_message(prediction)
        
        response = {
            'success': True,
            'prediction': prediction,
            'message': message
        }
        
        print("=== Sending Response ===")
        print(json.dumps(response, indent=2))
        print("=====================\n")
        
        return jsonify(response)
        
    except Exception as e:
        error_response = {
            'success': False,
            'error': str(e)
        }
        print("=== Error ===")
        print(json.dumps(error_response, indent=2))
        print("============\n")
        return jsonify(error_response), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)