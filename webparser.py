import requests
import argparse
import sys
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict
from collections import deque # Can also use a set if we care abt filtering abt duplicates, but I'm guessing the datasets are already scrubbed

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
            response = session.get(url, params=params, timeout=5, allow_redirects=True) # idk standard practice for timeouts
            
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
def HTMLparser(response: requests.Response) -> Optional[tuple[bool, bool, bool, bool]]:
    """
    Basically just checks for elements that would: 
    1) cause the status bar to be manipulated whenever an onMouseOver event occurs.
    (need to check inline + script event listeners)
    2) check for events that may lead to right click becoming disabled 
    3) 
    4) 

    Arguments: 
    response: Response object from connectionhandler

    Return:
    array of booleans: 

    """
    if not response or not response.content: #check to make sure the response obj is valid/there is actually webpage content
        return 
    statusBarChanged = False
    rightClickDisabled = False
    popUpWithText = False
    invisIframePresent = False
    soup = BeautifulSoup(response.content, 'html.parser') #creates a parse tree so we can look through HTML

    #found these lists online to identify patterns for certain events
    rightClickPatterns = [
        r'event\.button\s*==\s*2',           # event.button == 2
        r'event\.which\s*==\s*3',            # event.which == 3
        r'oncontextmenu\s*=\s*["\']return false',  # oncontextmenu="return false"
        r'preventDefault\(\)',                # e.preventDefault()
        r'return\s+false',                   # return false in event handlers
        r'button\s*===?\s*2',                # button === 2 or button == 2
        r'contextmenu',                      # contextmenu event
        r'mousedown.*button.*2',             # mousedown checking button 2
    ]
    popup_patterns = [
        r'window\.open\([^)]+\)',           # window.open() calls
        r'showModaldialog\([^)]+\)',        # showModalDialog() calls
        r'popup',                           # generic popup references
        r'modal',                           # modal windows
        r'dialog',                          # dialog windows
    ]
    input_field_patterns = [
        r'input.*type\s*=\s*["\']text["\']',    # <input type="text">
        r'textarea',                             # <textarea>
        r'contenteditable',                      # contenteditable elements
        r'prompt\([^)]+\)',                      
    ]
    
    # finds all (inline) onMouseOver elems that change status bar

    # syntax breakdown: checks for all elements that have the "onmouseover" attribute + matches the expression 
    # containg either "status" or "window.status", case insensitive (thats what re.I does)
    mouseOverElements = soup.find_all(attrs={"onmouseover": re.compile("status|window.status", re.I)}) 
    if len(mouseOverElements) != 0 :
        statusBarChanged = True


    # finds all events that may disable right click
    event_attributes = ['oncontextmenu', 'onmousedown', 'onmouseup', 'onclick']
    rightClickElems = [] # i guess we don't actually need this - can remove if we want to save memory 
    for attr in event_attributes:
        elements = soup.find_all(attrs={attr: re.compile('|'.join(rightClickPatterns), re.I)})
        rightClickElems.extend((elem, attr) for elem in elements)
    if len(rightClickElems) != 0 : 
        rightClickDisabled = True

    # finds elements that create pop up windows with text boxes
    modalDivs = soup.find_all('div', class_=re.compile('(modal|popup|dialog)', re.I))
    for div in modalDivs:
        inputs = div.find_all(['input', 'textarea']) + div.find_all(attrs={'contenteditable': True})
        if inputs:
            popUpWithText = True
            break
    elementsWithClick = soup.find_all(onclick=re.compile('|'.join(popup_patterns), re.I))
    if (len(elementsWithClick) != 0) :
        popUpWithText = True

    #checks if webpage has iframes + turns them invisible
    iframes = soup.find_all('iframe')
    for iframe in iframes:
        # check frameBorder attribute - can be 0/no/false 
        frameBorder = iframe.get('frameborder', '').lower()
        if frameBorder in ['0', 'no', 'false']:
            invisIframePresent = True
            break
        style = iframe.get('style', '').lower()
        if any(term in style for term in ['border: 0', 'border:0', 'border-width: 0', 'border-width:0', 'border: none', 'border:none']):
            invisIframePresent = True
            break

    # run through all scripts and check for changes 
    # can remove if everythign takes too long
    scripts = soup.find_all('script')
    for script in scripts:
        if not script.string: 
            continue
        if any(term in script.string.lower() for term in ['onmouseover', 'mouseover', 'window.status', 'status=']):
            statusBarChanged = True
        if any(re.search(pattern, script.string, re.I) for pattern in rightClickPatterns):
            rightClickDisabled = True
        for pattern in popup_patterns:
            matches = re.finditer(pattern, script.string, re.I)
            for match in matches:
                # need surrounding context
                start = max(0, match.start() - 100)
                end = min(len(script.string), match.end() + 100)
                context = script.string[start:end].strip()
                # then need to check if the popup code also contains input fields
                hasInput = any(re.search(input_pattern, context, re.I) for input_pattern in input_field_patterns)
                if hasInput:
                    popUpWithText = True
                    break
        if 'frameborder' in script.string.lower() and any(val in script.string.lower() for val in ['0', 'false', 'none']):
            invisIframePresent = True
    return statusBarChanged, rightClickDisabled, popUpWithText, invisIframePresent

while (urlDeque):
    currentSite = urlDeque.popleft()
    siteResponse = connectionHandler(currentSite) 

    if siteResponse:
        print(len(siteResponse.history))
        results = HTMLparser(siteResponse)
        if results:
            statusBar, rightClick, popUp, invisibleIframe = results
            print(f"Status bar manipulation: {statusBar}")
            print(f"Right click disabled: {rightClick}")
            print(f"Pop-up with text input: {popUp}")
            print(f"Invisible iframe present: {invisibleIframe}")


