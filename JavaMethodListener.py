from ANTLR.Java20ParserListener import Java20ParserListener
from References import RefHandler

class JavaMethodListener(Java20ParserListener):
    def __init__(self, parser):
        self.currentClass: str = None
        self.refHandler = RefHandler()
    
    # === TYPE DECLARATIONS ===
    def enterNormalClassDeclaration(self, ctx):
        self.currentClass = ctx.typeIdentifier().getText()
        self.refHandler.classInit(self.currentClass)
    
    def enterFieldDeclaration(self, ctx):
        uReferenceType = ctx.unannType().unannReferenceType()
        if uReferenceType != None:
            # Differentiate between class/interface and arrays
            uClassOrInterfaceType = uReferenceType.unannClassOrInterfaceType()
            typeName = uClassOrInterfaceType.typeIdentifier().getText() if uClassOrInterfaceType != None else uReferenceType.unannArrayType() # Array workaround
        else:
            # Primitive type-- not a class
            # typeName = ctx.unannType().unannPrimitiveType().getText()
            return
        
        self.refHandler.classInit(typeName)
        
        varDeclaratorList = ctx.variableDeclaratorList()

        for varDeclarator in varDeclaratorList.variableDeclarator():
            typeID = varDeclarator.variableDeclaratorId().getText()
            self.refHandler.addClassInstance(typeName,typeID)

    def enterLocalVariableDeclaration(self, ctx):
        # typeName = ctx.localVariableType().unannType().unannReferenceType().unannClassOrInterfaceType().typeIdentifier().getText()
        uReferenceType = ctx.localVariableType().unannType().unannReferenceType()
        if uReferenceType != None:
            # Differentiate between class/interface and arrays
            uClassOrInterfaceType = uReferenceType.unannClassOrInterfaceType()
            typeName = uClassOrInterfaceType.typeIdentifier().getText() if uClassOrInterfaceType != None else uReferenceType.unannArrayType() # Array workaround
            #typeName = uReferenceType.unannClassOrInterfaceType().typeIdentifier().getText()
        else:
            # Primitive type-- not a class
            # typeName = ctx.localVariableType().unannType().unannPrimitiveType().getText()
            return
        
        self.refHandler.classInit(typeName)
        
        varDeclaratorList = ctx.variableDeclaratorList()

        for varDeclarator in varDeclaratorList.variableDeclarator():
            typeID = varDeclarator.variableDeclaratorId().getText()
            self.refHandler.addClassInstance(typeName,typeID)

    def enterCatchFormalParameter(self, ctx):
        typeName = ctx.catchType().getText()
        typeID = ctx.variableDeclaratorId().getText()
        self.refHandler.addClassInstance(typeName,typeID)

    # TODO: Arity Parameter? (FieldFactory.java)

    # === METHOD DECLARATIONS ===
    def enterMethodDeclaration(self, ctx):
        methodName = ctx.methodHeader().methodDeclarator().Identifier().getText()
        #typeName = self.refHandler.fetchType()
        self.refHandler.addMethodRef(self.currentClass, methodName)
    
    def enterMethodInvocation(self, ctx):
        methodNameCtx = ctx.Identifier()
        #methodName = methodNameCtx.getText() if methodNameCtx != None else ""
        
        if methodNameCtx is not None:
            methodName = methodNameCtx.getText()
            startToken = ctx.start
            lineNumber = startToken.line
            
            #Check if this method was explicitly called by a class
            #prefix = ctx.expressionName()
            prefix = ctx.typeName()

            if ((prefix != None) or (prefix == "this")):
                typeIdentifier = prefix.getText()
            else:
                # Primitive type-- not a class
                return
                # print("==no prefix found")
                # typeIdentifier = self.currentClass
            
            className = self.refHandler.identifierToType(typeIdentifier)
            
            self.refHandler.addMethodRef(className, methodName)

            # print("Method invocation: %s.%s (%s)" % (className, methodName, self.currentClass))
            # print("   Line: %d" % lineNumber)