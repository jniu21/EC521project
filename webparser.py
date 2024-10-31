import requests
import argparse
import sys
from typing import Optional, Dict
from collections import deque # Can also use a set if we care abt filtering abt duplicates, but I'm guessing the datasets are already scrubbed
print(sys.version)
urlDeque = deque(maxlen = 500) # Uhhh change number later - arbitrary 

def connectionHandler(url: str, params: Optional[Dict[str,str]] = None) -> Optional[requests.Response]:
    """
    Reads in a url

    Arguments(? idk are these parameters too): 
    url (str): The url of the website being connected to 
    params: Optional parameters for connection to site 


    Return:
    requests.Response: a Response object containing info pertaining to the server's response (or None if no response)

    """
    try:
        with requests.Session() as session:
            response = session.get(url, params=params, timeout=10) # idk standard practice for timeouts
            
            #maybe need to add headers here/other parameters to check robots.txt file and whatnot

            response.raise_for_status()
            return response 
    except requests.exceptions.HTTPError as http_error:
        print(f"HTTP error occurred: {http_error}")
    except requests.exceptions.ConnectionError as connect_error:
        print(f"Connection error occurred: {connect_error}")
    except requests.exceptions.Timeout:
        print("The request timed out!")
    except requests.exceptions.RequestException as request_error:
        print(f"An error has occurred: {request_error}")
    
    return None # In cas e an error occurs

#def parserOfSomeSort()
# We should definitely split this into two files but that's a later issue 

# Get the text file from command line 
argParser = argparse.ArgumentParser(description = "Website Parsing")
argParser.add_argument("-urlList", type=str, help="Path to a text file containing URLs")
argParser.add_argument("-url", type=str, help="URL to be examined")

# Make sure that the user passes arguments to command line 
if len(sys.argv) == 1:
    argParser.print_help()
    sys.exit("No arguments provided. Please use -url or -urlList to specify URLs to parse.")
else: 
    args = argParser.parse_args()

# ummmm yeah idk smthj goes here
if args.url: 
    print("Handling one URL:", args.url)
    urlDeque.append(args.url)
elif args.urlList:
    print("Processing URLs from file: ", args.urlList)
    with open(args.urlList, "r") as file:
        urls = file.readlines()
        for url in urls: 
            urlDeque.append(url.strip())

# ----Parsing region----- 
currentSite = urlDeque.popleft()
siteResponse = connectionHandler(currentSite) # then analyze the json/headers/whatever
print(siteResponse.headers)


