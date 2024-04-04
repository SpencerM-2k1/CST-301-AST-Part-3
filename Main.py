import sys
import antlr4

from ANTLR.Java20Lexer import Java20Lexer
from ANTLR.Java20Parser import Java20Parser

from DocFetch import DocFetch
from FileHandler import FileHandler

from JavaMethodListener import JavaMethodListener

# === EXECUTION START ===
# Launch arguments            
filePath = ""
if(len(sys.argv) > 1):
    filePath = sys.argv[1]
else:
    # Default test file, commented files for convenience in repeated testing
    filePath = "assets/AssignmentSample.java"
    # filePath = "assets/AutosaveManager.java"
    # filePath = "assets/BindingsHelper.java"
    # filePath = "assets/ClipBoardManager.java"
    # filePath = "assets/CrossRef.java"
    # filePath = "assets/DefaultLatexParser.java"
    # filePath = "assets/DefaultTexParserTest.java"
    # filePath = "assets/ExternalFilesEntryLinker.java"
    # filePath = "assets/FieldFactory.java"
    # filePath = "assets/JabRefFrame.java" # WARNING: EXCEPTIONALLY LONG EXECUTION TIME
    # filePath = "assets/PreviewViewer.java" # Fails to parse correctly due to triple quotes
    # filePath = "assets/PreviewViewer(redacted).java" 

# Load .java file
inputString = FileHandler.loadText(filePath)

# Parse
inputStream = antlr4.InputStream(inputString)
lexer = Java20Lexer(inputStream)
tokens = antlr4.CommonTokenStream(lexer)
parser = Java20Parser(tokens)
tree = parser.compilationUnit()

walker = antlr4.ParseTreeWalker()
listener = JavaMethodListener(parser)
walker.walk(listener, tree)

print()
print("listener.refHandler: %s" % listener.refHandler)

# Relate identifiers to their class types, find all methods called for each class type
docFetch = DocFetch(listener.refHandler.classDict)
docFetch.getLinks()
print()
print("docFetch: %s" % docFetch)

# Save fetched descriptions and tags
saveDir = "outputs/" + FileHandler.pathToFilename(filePath)
# FileHandler.saveText("bababooey",savePath)
docFetch.fetchAllDocs(saveDir)