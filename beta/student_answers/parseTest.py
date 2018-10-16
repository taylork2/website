import ast 
import sys
import StringIO

expr = """
def goodbye(a,b,c):
	print("Hello World!")

def hello(d):
	return "hello"

goodbye(1,2,3)
"""

fxn_name = "goodbye"
params = ['a', 'b' ]
reqs = {"for":5, "print":2, "while":1}
testcase = "goodbye(1,2,3)"

p = ast.parse(expr)

# create file-like string to capture output
codeOut = StringIO.StringIO()
codeErr = StringIO.StringIO()

# capture output and errors
sys.stdout = codeOut
sys.stderr = codeErr

# exec code VERY DANGEROUS NEED TO FIND BETTER WAY!!! 
exec(compile(p, filename="<ast>", mode="exec"))

# restore stdout and stderr
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

s = codeErr.getvalue()

print "error:\n%s\n" % s

s = codeOut.getvalue()

print "output:\n%s" % s

codeOut.close()
codeErr.close()


class AllNodes(ast.NodeVisitor):
	def generic_visit(self, node):
		print type(node).__name__
		ast.NodeVisitor.generic_visit(self, node)

class FuncLister(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print(node.name)
        self.generic_visit(node)

class ArgLister(ast.NodeVisitor):
    def visit_arguments(self, node):
    	for i in node.args: 
        	print(i.id)
        self.generic_visit(node)

def checkFuncDef(tree, fxnName):
	initialFuncDef = None
	for node in ast.walk(tree):
	    if isinstance(node, ast.FunctionDef):
	    	if str(node.name) == fxnName:
	    		return True, node
	    	initialFuncDef = node
	return False, initialFuncDef

def checkParamNames(tree, params): 
	for node in ast.iter_child_nodes(tree):
	    if isinstance(node, ast.arguments):
	    	for arg in node.args: 
	    		if str(arg.id) not in params:
	    			return False
	return True

def checkParamTotal(tree, params):
	for node in ast.iter_child_nodes(tree):
		if isinstance(node, ast.arguments):
			if len(node.args) != len(params):
				return False, abs(len(node.args)-len(params))
	return True, 0

def rewriteFuncDef(tree, funcName):
	class RewriteFunction(ast.NodeTransformer):
	    def visit_FunctionDef(self, node):

	        return ast.copy_location(ast.FunctionDef(
	        	name = funcName, 
	        	args = node.args,
	        	body = node.body,
	        	decorator_list = node.decorator_list
	        	), node)

	RewriteFunction().visit(tree)
	return tree

def rewriteParams(tree, params):
	class RewriteParam(ast.NodeTransformer):
		def visit_arguments(self, node):
			astArgsArray = []
			for i in params:
					astArgsArray.append(ast.Name(id=i, ctx=ast.Param()))
		        
			return ast.copy_location(ast.arguments(args = astArgsArray, varargs = None, defaults = None), node)

	RewriteParam().visit(tree)
	return tree 

def checkReqs(tree, reqs):
	reqsMatch = False
	for node in ast.walk(tree):
		if "for" in reqs and isinstance(node, ast.For):
			del reqs["for"]
			continue
		
		if "while" in reqs and isinstance(node, ast.While):
			del reqs["while"]
			continue

		if "print" in reqs and isinstance(node, ast.Print):
			del reqs["print"]
			continue	

		if "def" in reqs and isinstance(node, ast.FunctionDef):
			del reqs["def"]
			continue

		if "if" in reqs and isinstance(node, ast.If):
			del reqs["if"]
			continue

		if "return" in reqs and isinstance(node, ast.Return):
			del reqs["return"]
			continue

	if len(reqs) == 0: 
		reqsMatch = True

	return reqsMatch, reqs

def scoreMissingReqs(missingReqs, score):
	for i in missingReqs.values():
		score -= i 
		if score <= 0:
			return 0 
	return score 

# class TestCase(tree, testCaseStr):
# 	cases = testCaseStr.split("///")
# 	method = cases[0]
# 	expectedResult = cases[1]
# 	points = cases[2]
# 	p = tree

# 	# True if test case passes, False otherwise 
# 	def runCase():
# 		try:
# 			exec(compile(p, filename="<ast>", mode="exec"))
# 		except:
# 			return False, "Does not compile"
# 		return True

	# def checkCase():
		# exec(compile(tree, filename="<ast>", mode="exec"))





# try:
# 	p = ast.parse(expr)
# except:
# 	points = points - points*0.9
# 	print points 
# 	return

p = ast.parse(expr)
points = 10

# Check the function name 
funcDefMatch, funcDefNode = checkFuncDef(p, fxn_name)
print funcDefMatch
if not funcDefMatch: 
	points -= 1 
	p = rewriteFuncDef(p, fxn_name)
	FuncLister().visit(p)

# Check the parameters 
paramTotalMatch, paramTotalDif = checkParamTotal(funcDefNode, params)
paramNamesMatch = checkParamNames(funcDefNode, params)
print funcDefMatch, paramTotalMatch, paramNamesMatch 
if not paramTotalMatch or not paramNamesMatch:
	points -= 1
	p = rewriteParams(p, params)
	ArgLister().visit(p)

# Check the requirements 
print "for" in reqs
reqsMatch, missingReqs = checkReqs(p, reqs)
print "reqs: ",reqsMatch,len(missingReqs)
points = scoreMissingReqs(missingReqs, points)

print "points: ", points

