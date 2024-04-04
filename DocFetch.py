import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin

# from message import ask_gpt
from Classifier import getTags
from FileHandler import FileHandler

class DocFetch():
    def __init__(self, classDict):
        self.classDict = classDict
        self.linkDict = {} # {typeName : (URL, [functions])}

    # Create a list of doc pages to fetch
    def getLinks(self):
        for className, functions in self.classDict.items():
            link = DocFetch.fetchDocLink(className)
            if link:
                self.linkDict[className] = (link, functions)

    # Find the link to a class's documentation
    #   (Currently supports Java, JavaFX, ControlsFX)
    def fetchDocLink(query):
        # returnLink = DocFetch.fetchJavaLink(query)
        returnLink = DocFetch.fetchLink(query,"https://docs.oracle.com/javase/8/docs/api/","allclasses-noframe.html")
        if returnLink:
            return returnLink
        # returnLink = DocFetch.fetchJavaFXLink(query)
        returnLink = DocFetch.fetchLink(query,"https://docs.oracle.com/javase/8/javafx/api/","allclasses-noframe.html")
        if returnLink:
            return returnLink
        # returnLink = DocFetch.fetchControlsFXLink(query)
        returnLink = DocFetch.fetchLink(query,"https://controlsfx.github.io/javadoc/11.1.2/","allclasses.html")
        if returnLink:
            return returnLink
        print("DEBUG: No documentation found for `%s`." % query)
        return None

    def fetchLink(query, rootURL, indexDir):
        # URL of the Java documentation website
        # rootURL = "https://docs.oracle.com/javase/8/docs/api/"

        # allclasses-noframe.html contains a link to all Java classes
        indexUrl = rootURL + indexDir

        # Send HTTP GET request
        response = requests.get(indexUrl)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links in the main page
            links = soup.find_all('a', href=True)
            for link in links:
                # Check if the query is in the link text
                if query == (link.text):
                    # Assemble URL for the documentation link
                    docLink = urljoin(rootURL, link['href'])
                    print("DEBUG: Documentation found for `%s`." % query)
                    return docLink
            
            return None 
        else:
            print("ERROR: Failed to reach the documentation website.")
            return None
    
    def __str__(self):
        #return str(self.classRefs)
        return str(self.classDict) + "\n" + str(self.linkDict)

    # Fetch class/method info 
    def fetchClassDescription(docLink):
        # HTTP GET request
        response = requests.get(docLink)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the element containing the class description
            classDesc = soup.find('div', {'class': 'description'})
            
            if classDesc:
                # Extract and return the text of the class description
                blocks = classDesc.find_all('div', {'class': 'block'})
                # blockTexts = [block.get_text(separator="\n").strip() for block in blocks]
                # blockTexts = [block.get_text().strip() for block in blocks]
                blockTexts = ""
                for block in blocks:
                    if block.get_text() != "\n":
                        blockTexts += block.get_text().strip()

                return blockTexts
            else:
                return "No description found for the class."
        else:
            return "Failed to fetch data from the documentation website."
    
    # Fetch class/method info 
    def fetchMethodDescription(docLink, methodName):
        # HTTP GET request
        response = requests.get(docLink)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            methodHeaders = DocFetch.getMethodHeaders(soup)

            for methodHeader in methodHeaders:
                if methodHeader.text == methodName:
                    return methodHeader.find_next_sibling('div', {'class': 'block'}).get_text().strip()
            return "Method %s was not found within the documentation (might be inherited)." % (methodName)
        else:
            return "Failed to fetch data from the documentation website."
    
    def getMethodHeaders(soup):
        # Find all comments in the HTML
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))

        # Iterate through the comments and check for "METHOD DETAIL"
        for comment in comments:
            if "METHOD DETAIL" in comment:
                methodHeaders = comment.find_all_next('h4', text=True)
                # for header in methodHeaders:
                #     print(header.text)
                return methodHeaders
        return None # No method detail found-- may result in error

    # Iterate through all classes/functions in linkDict, print them to their respective files
    #   Also, get a list of classification tags w/ justification from G4F
    def fetchAllDocs(self, rootSaveDir):
        dirTimestamp = datetime.fromtimestamp(int(time.time())).strftime("%Y-%m-%d_%H-%M-%S")
        for className, entry in self.linkDict.items():
            docLink = entry[0]
            methodList = entry[1]
            classSaveDir = rootSaveDir + "/" + dirTimestamp + "/" + className + "/"
            classDescription = DocFetch.fetchClassDescription(docLink)
            # FileHandler.saveText(classDescription, classSaveDir + "!CLASSDESC.txt")
            
            # Use g4f to classify classes and functions-- append as tags at end of file
            gptClassResponse = getTags(classDescription, "Class: " + className)
            g4fClassAppend = "\n\n=== CLASS TAGS ===\n"
            for chunk in gptClassResponse:
                if chunk.choices[0].delta.content:
                    g4fClassAppend += (chunk.choices[0].delta.content.strip('*') or "")
            
            # FileHandler.appendText(classDescription + g4fClassAppend, classSaveDir + "!CLASSDESC.txt")
            FileHandler.saveText(classDescription + g4fClassAppend, classSaveDir + "!CLASSDESC.txt")

            for methodName in methodList:
                methodDescription = DocFetch.fetchMethodDescription(docLink, methodName)
                gptMethodResponse = getTags(methodDescription, "Method: " + className + "." + methodName)
                g4fMethodAppend = "\n\n=== METHOD TAGS ===\n"
                for chunk in gptMethodResponse:
                    if chunk.choices[0].delta.content:
                        g4fMethodAppend += (chunk.choices[0].delta.content.strip('*') or "")

                FileHandler.saveText(methodDescription + g4fMethodAppend, classSaveDir + methodName + ".txt")
