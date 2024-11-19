#!/usr/bin/env python3

import pandas as pd

def transform_url_length(value):
    """
    Transform URL length according to the rules:
    < 54: 1 (legitimate)
    54-75: 0 (suspicious)
    > 75: -1 (phishing)
    """
    try:
        value = float(value)  
        if value < 54:
            return 1
        elif 54 <= value <= 75:
            return 0
        else:
            return -1
    except (ValueError, TypeError):
        return None  # Return None for any invalid values
    
def transform_having_subdomain(value):
    try:
        value = float(value)  
        if value == 1 :
            return 1
        if value == 2 :
            return 0
        else:
            return -1
    except (ValueError, TypeError):
        return None

def transform_domain_registration_length(value):
    try:
        value = float(value)  
        if value < 365:
            return -1
        else:
            return 1
    except (ValueError, TypeError):
        return None
    
def transform_Request_URL(value):
    try:
        if value == 'Suspicious':
            return 0
        if value == 'Legitimate':
            return 1
        else:
            return -1
    except (ValueError, TypeError):
        return None

def transform_URL_of_Anchor(value):
    try:
        if value == 'Suspicious':
            return 0
        if value == 'Legitimate':
            return 1
        else:
            return -1
    except (ValueError, TypeError):
        return None
    
def transform_Links_in_tags(value):
    try:
        value = float(value) 
        if value < 17:
            return 1
        if value < 81 :
            return 0
        else:
            return -1
    except (ValueError, TypeError):
        return None
    
def transform_SFH(value):
    try:
        if value == 'Suspicious':
            return 0
        if value == 'Legitimate':
            return 1
        else:
            return -1
    except (ValueError, TypeError):
        return None

def transform_age_of_domain(value):
    try:
        value = float(value)  
        if value == -1:
            return -1
        if value > 180 :
            return 1
        else:
            return 0
    except (ValueError, TypeError):
        return None
    
def transform_web_traffic(value):
    try:
        value = float(value)
        if value < 100000:
            return 1
        if value >= 100000 :
            return 0
        else:
            return -1
    except (ValueError, TypeError):
        return None
    
def transform_Page_Rank(value):
    return value

def transform_Links_pointing_to_page(value):
    try: 
        value = float(value)
        if value == 0:
            return -1
        if value < 2:
            return 0
        else:
            return 1
    except (ValueError, TypeError):
        return None
    
def transform_Result(value):
    try:
        if value == 'phishing':
            return -1
        if value == 'legitimate':
            return 1
        else:
            return 0
    except (ValueError, TypeError):
        return None
    


def process_dataset(input_file, output_file):
    """
    Process the parsed CSV file and transform URL length values.
    """
    try:
        df = pd.read_csv(input_file)
        
        new_df = df.copy()
        
        # Transform URL_Length column
        new_df['URL_Length'] = df['URL_Length'].apply(transform_url_length)
        new_df['having_Sub_Domain'] = df['having_Sub_Domain'].apply(transform_having_subdomain)
        new_df['Domain_registeration_length'] = df['Domain_registeration_length'].apply(transform_domain_registration_length)
        new_df['Request_URL'] = df['Request_URL'].apply(transform_Request_URL)
        new_df['URL_of_Anchor'] = df['URL_of_Anchor'].apply(transform_URL_of_Anchor)
        new_df['Links_in_tags'] = df['Links_in_tags'].apply(transform_Links_in_tags)
        new_df['SFH'] = df['SFH'].apply(transform_SFH)
        new_df['age_of_domain'] = df['age_of_domain'].apply(transform_age_of_domain)
        new_df['web_traffic'] = df['web_traffic'].apply(transform_web_traffic)
        new_df['Page_Rank'] = df['Page_Rank'].apply(transform_Page_Rank)
        new_df['Links_pointing_to_page'] = df['Links_pointing_to_page'].apply(transform_Links_pointing_to_page)
        new_df['Result'] = df['Result'].apply(transform_Result)

        
        # Save to new CSV file
        new_df.to_csv(output_file, index=False)
        
        print(f"Successfully transformed CSV with {len(new_df)} rows")
        
    except Exception as e:
        print(f"Error processing dataset: {str(e)}")
        raise


if __name__ == "__main__": 
    input_file = "RAW_Parsed.csv"
    output_file = "transformed_dataset.csv"
    
    process_dataset(input_file, output_file)