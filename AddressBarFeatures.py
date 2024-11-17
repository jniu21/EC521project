import pandas as pd
from urllib.parse import urlparse
import re
from datetime import datetime

def process_urls_from_csv(input_csv_path, output_csv_path='url_features.csv'):
    """
    Read URLs from input CSV, extract features, and save to output CSV.
    
    Args:
        input_csv_path (str): Path to input CSV file containing URLs
        output_csv_path (str): Path where output CSV will be saved
    
    Returns:
        pandas.DataFrame: DataFrame containing all features
    """
    # Read URLs from CSV
    try:
        # Try reading CSV assuming URLs are in a column named 'url' or 'URL'
        try:
            df_urls = pd.read_csv(input_csv_path)
            url_column = next(col for col in df_urls.columns if col.lower() == 'url')
            urls = df_urls[url_column].tolist()
        except StopIteration:
            # If no 'url' column found, assume first column contains URLs
            df_urls = pd.read_csv(input_csv_path)
            urls = df_urls.iloc[:, 0].tolist()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

    # Initialize list to store all feature dictionaries
    all_features = []
    
    # Process each URL
    for idx, url in enumerate(urls, 1):
        try:
            parsed = urlparse(url)
            
            # Get features for this URL
            features = {
                'index': idx,
                'URL': url,
                'having_IPhaving_IP_Address': check_ip_address(parsed.netloc),
                'URLURL_Length': 1 if len(url) < 54 else (0 if len(url) <= 75 else -1),
                'Shortining_Service': check_shortening_service(parsed.netloc),
                'having_At_Symbol': -1 if '@' in url else 1,
                'double_slash_redirecting': -1 if '//' in parsed.path else 1,
                'Prefix_Suffix': -1 if '-' in parsed.netloc else 1,
                'having_Sub_Domain': check_subdomain(parsed.netloc),
                'SSLfinal_State': check_ssl(url),
                'Domain_registeration_length': check_domain_registration(parsed.netloc),
                'Favicon': check_favicon(parsed.netloc, url),
                'port': check_port(parsed.netloc),
                'HTTPS_token': -1 if 'https' in parsed.netloc or 'http' in parsed.netloc else 1
            }
            
            all_features.append(features)
            
            # Print progress every 100 URLs
            if idx % 100 == 0:
                print(f"Processed {idx} URLs...")
                
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            # Add row with error values
            features = {
                'index': idx,
                'URL': url,
                'having_IPhaving_IP_Address': -1,
                'URLURL_Length': -1,
                'Shortining_Service': -1,
                'having_At_Symbol': -1,
                'double_slash_redirecting': -1,
                'Prefix_Suffix': -1,
                'having_Sub_Domain': -1,
                'SSLfinal_State': -1,
                'Domain_registeration_length': -1,
                'Favicon': -1,
                'port': -1,
                'HTTPS_token': -1
            }
            all_features.append(features)
    
    # Convert to DataFrame
    df_features = pd.DataFrame(all_features)
    
    # Save to CSV
    df_features.to_csv(output_csv_path, index=False)
    print(f"\nFeatures saved to {output_csv_path}")
    
    return df_features

def check_ip_address(domain):
    """Check if domain contains IP address."""
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    try:
        if re.match(ip_pattern, domain.split(':')[0]):
            return -1
        return 1
    except:
        return 1

def check_shortening_service(domain):
    """Check if URL uses a shortening service."""
    shortening_services = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'is.gd', 'cli.gs', 'ow.ly']
    return -1 if any(service in domain.lower() for service in shortening_services) else 1

def check_subdomain(domain):
    """Check number of subdomains."""
    if not domain:
        return 0
    dots = len(domain.split('.')) - 2
    if dots == 1:
        return 1
    elif dots == 2:
        return 0
    return -1 if dots > 2 else 1

def check_ssl(url):
    """Check SSL certificate."""
    return 1 if url.startswith('https') else -1

def check_domain_registration(domain):
    """Simplified domain registration check."""
    try:
        return 1 if len(domain) > 10 else -1
    except:
        return -1

def check_favicon(domain, url):
    """Check if favicon is loaded from same domain."""
    try:
        return 1 if domain in url else -1
    except:
        return -1

def check_port(netloc):
    """Check if default port is used."""
    try:
        if ':' in netloc:
            port = int(netloc.split(':')[1])
            if port != 80 and port != 443:
                return -1
        return 1
    except:
        return -1
