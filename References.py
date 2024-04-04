# Handles a specialized dictionary for method calls
# Each RefHandler instance is only suited to ONE class body
#   
class RefHandler():
    def __init__(self):
        # List of class instances
        self.classInstances: dict = {} #key: value = str
        
        # List of classes to attempt to find documentation for
        #   If value list is not empty, look up specific functions listed, too
        self.classDict: dict = {} #key: value = list
    
    # Register identifier to be recognized as a class instance
    def addClassInstance(self, typeName: str, typeID: str):
        # Note to self: think of it like a pointer relationship
        #   identifier -> typeName, keep this order for dict
        self.classInstances[typeID] = typeName
        print("%s is an instance of class %s" % (typeID, typeName))

    # # Start tracking a class's functions
    def classInit(self, typeName: str):
        # Only init class type if it is not yet registered
        if self.isRegistered(typeName) == False:
            print("==ADDING %s TO REGISTRY==" % (typeName))
            self.classDict[typeName] = set() #Set-- no duplicates
    
    # # Check if class is being tracked
    def isRegistered(self, typeName: str):
        return typeName in self.classDict

    # Link a method name to its associated class
    def addMethodRef(self, typeName: str, methodID: str):
        self.classInit(typeName)

        if methodID in self.classDict[typeName]:
            #print("REDUNDANCY: %s in class %s is already registered" % (methodID, typeName))
            pass
        else:
            print("%s belongs to class %s" % (methodID, typeName))
            pass
        self.classDict[typeName].add(methodID)
        # print("Method: %s belongs to class %s" % (methodID, typeName))

    def identifierToType(self, identifier):
        # Search for an exact match in classDict
        if identifier in self.classDict:
            return identifier

        # Search for a matching identifier among classInstances
        if identifier in self.classInstances:
            return self.classInstances[identifier]

        # Else, failure
        return None

    def __str__(self):
        #return str(self.classRefs)
        return str(self.classInstances) + "\n" + str(self.classDict)