import requests
from bs4 import BeautifulSoup
import tldextract
import pandas as pd

#most convenient dataset:https://www.kaggle.com/datasets/shashwatwork/web-page-phishing-detection-dataset/data
#integrate with this one:https://www.kaggle.com/code/akashkr/phishing-url-eda-and-modelling/notebook

# Load URLs dataset
# Assuming you have a CSV with a column 'url'
url_df = pd.read_csv('C:/Users/biray/OneDrive/Masaüstü/Boston University/COURSES/EC521/project/truncated_file.csv')
url_df2 = pd.read_csv('C:/Users/biray/OneDrive/Masaüstü/Boston University/COURSES/EC521/project/adressbarfeatures.csv')

#url_df = url_df

def extract_features(url):
    features = {
        'Request_URL': None,
        'URL_of_Anchor': None,
        'SFH': None
    }
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the main domain of the URL for comparison
        main_domain = tldextract.extract(url).domain
        
        # Feature 1: Request URL
        external_object_count = 0
        total_object_count = 0
        
        for tag in soup.find_all(['img', 'video', 'audio', 'iframe']):
            src = tag.get('src')
            if src:
                total_object_count += 1
                object_domain = tldextract.extract(src).domain
                if object_domain and object_domain != main_domain:
                    external_object_count += 1
                    
        # Calculate percentage of external objects
        if total_object_count > 0:
            external_obj_percentage = (external_object_count / total_object_count) * 100
            if external_obj_percentage < 22:
                features['Request_URL'] = 1
            elif 22 <= external_obj_percentage <= 61:
                features['Request_URL'] = '0
            else:
                features['Request_URL'] = -1
        
        # Feature 2: URL of Anchor
        external_anchor_count = 0
        total_anchor_count = 0
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            total_anchor_count += 1
            anchor_domain = tldextract.extract(href).domain
            if anchor_domain and anchor_domain != main_domain:
                external_anchor_count += 1
        
        # Calculate percentage of external anchors
        if total_anchor_count > 0:
            external_anchor_percentage = (external_anchor_count / total_anchor_count) * 100
            if external_anchor_percentage < 31:
                features['URL_of_Anchor'] = 1
            elif 31 <= external_anchor_percentage <= 67:
                features['URL_of_Anchor'] = 0
            else:
                features['URL_of_Anchor'] = -1
        
        # Feature 3: Server Form Handler (SFH)
        sfh = soup.find('form', action=True)
        if sfh:
            action = sfh['action']
            if action in ["about:blank", ""]:
                features['SFH'] = -1
            elif tldextract.extract(action).domain != main_domain:
                features['SFH'] = 0
            else:
                features['SFH'] = 1
        else:
            features['SFH'] = 1  # No form means no external handler
        
    except Exception as e:
        print(f"Failed to process {url}: {e}")
    
    return features

# Apply the feature extraction function to each URL
feature_data = []
for url in url_df['url']:
    feature_data.append(extract_features(url))

# Create a DataFrame with the results
features_df = pd.DataFrame(feature_data)
output_df = pd.concat([url_df, features_df], axis=1)

# Save the results to a CSV
output_df.to_csv('url_features_extracted_all_2.csv', index=False)

print("Feature extraction completed and saved to 'url_features_extracted.csv'.")

import whois
from urllib.parse import urlparse

def classify_website_by_url(url):
    try:
        # Parse the URL to extract the host name
        parsed_url = urlparse(url)
        host_name = parsed_url.netloc
        
        # Query the WHOIS database
        whois_info = whois.whois(host_name)

        # Decode fields if they are in bytes
        registrar_name = whois_info.registrar
        organization_name = whois_info.org
        print(registrar_name + "   " + host_name + " " + organization_name)
        # Extract the registrar or owner info
        registrar_name = whois_info.registrar or ""
        organization_name = whois_info.org or ""
        # Check if the host name is included in the WHOIS data
        if host_name in registrar_name or host_name in organization_name:
            return "Legitimate"
        else:
            return "Phishing"
    except Exception as e:
        return f"Error processing the website: {e}"

# Example usage
# Example Usage

# Update the "Abnormal_URL" column with classification results
url_df['URL'].apply(classify_website_by_url)



