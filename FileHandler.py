import os

# Save/load files
#   Inefficient due to frequent open/close, but used for readability for now
class FileHandler():
    def loadText(filePath):
        f = open(filePath, "r")
        fileString = f.read()
        f.close()
        return fileString
    
    def saveText(fileString, filePath):
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        f = open(filePath, "w")
        f.write(fileString)
        f.close
        return None
    
    def appendText(fileString, filePath):
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        f = open(filePath, "a")
        f.write(fileString)
        f.close
        return None
    
    def pathToFilename(filePath):
        return filePath.replace("/",".")
