#!/usr/bin/env python3

import pandas as pd

def process_dataset(input_file, output_file):
    """
    Creates new CSV with specified columns in exact order.
    """
    try:
        # Read input CSV
        df = pd.read_csv(input_file)
        
        # Define the exact order of columns we want and their mappings from input
        ordered_columns = [
            ('index', None),  # Will be added as row index
            ('having_IP_Address', 'ip'),
            ('URL_Length', 'length_url'),
            ('Shortining_Service', 'shortening_service'),
            ('having_At_Symbol', 'nb_at'),
            ('double_slash_redirecting', 'nb_dslash'),
            ('Prefix_Suffix', 'prefix_suffix'),
            ('having_Sub_Domain', 'nb_subdomains'),
            ('SSLfinal_State', 'https_token'),
            ('Domain_registeration_length', 'domain_registration_length'),
            ('Favicon', 'external_favicon'),
            ('port', 'port'),
            ('HTTPS_token', 'https_token'),
            ('Request_URL', 'Request_URL'),
            ('URL_of_Anchor', 'URL_of_Anchor'),
            ('Links_in_tags', 'links_in_tags'),
            ('SFH', 'sfh'),
            ('Submitting_to_email', 'submit_email'),
            ('Abnormal_URL', 'abnormal_subdomain'),
            ('Redirect', 'nb_redirection'),
            ('on_mouseover', 'onmouseover'),
            ('RightClick', 'right_clic'),
            ('popUpWidnow', 'popup_window'),
            ('Iframe', 'iframe'),
            ('age_of_domain', 'domain_age'),
            ('DNSRecord', 'dns_record'),
            ('web_traffic', 'web_traffic'),
            ('Page_Rank', 'page_rank'),
            ('Google_Index', 'google_index'),
            ('Links_pointing_to_page', 'nb_hyperlinks'),
            ('Statistical_report', 'statistical_report'),
            ('Result', 'status')
        ]
        
        # Create new dataframe with index
        new_df = pd.DataFrame()
        new_df['index'] = range(len(df))
        
        # Add each column in specified order
        for new_col, old_col in ordered_columns[1:]:  # Skip 'index' as we already added it
            if old_col in df.columns:
                new_df[new_col] = df[old_col]
            else:
                new_df[new_col] = None  # Add empty column if input column doesn't exist
        
        # Save to new CSV file
        new_df.to_csv(output_file, index=False)
        
        print(f"Successfully created new CSV with {len(new_df)} rows")
        print(f"Columns in order: {', '.join(new_df.columns)}")
        
    except Exception as e:
        print(f"Error processing dataset: {str(e)}")
        raise

if __name__ == "__main__": 
    input_file = './RAWData.csv'
    output_file = "./RAW_Parseded.csv"
    process_dataset(input_file, output_file)