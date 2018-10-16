import ast 
import sys
import StringIO

# Functions for displaying data  
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

# CHECK MATCHING DEF & PARAMS ========================
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
			newNode = ast.FunctionDef(
				name = funcName, 
				args = node.args, 
				body = node.body,
				decorator_list = node.decorator_list)
			ast.copy_location(newNode, node)
			ast.fix_missing_locations(newNode)	
			return newNode
	RewriteFunction().visit(tree)
	return tree
	
def rewriteParams(tree, params):
	class RewriteParam(ast.NodeTransformer):
		def visit_arguments(self, node):
			astArgsArray = []
			for i in params:
				astArgsArray.append(ast.Name(id=i, ctx=ast.Param()))
			
			newNode = ast.arguments(
				args = astArgsArray, 
				varargs = None, 
				defaults = node.defaults)

			ast.copy_location(newNode, node)
			ast.fix_missing_locations(newNode)
			return newNode

	RewriteParam().visit(tree)
	return tree 

# CHECK MATCHING REQS ====================================
def createReqDict(reqs):
	reqsDict = {}
	reqsArray = reqs.split("///")
	for i in range(0, len(reqsArray)-1, 2):
		reqsDict[reqsArray[i]] = int(reqsArray[i+1]) 

	return reqsDict

def checkReqs(tree, reqs):
	reqsMatch = False
	for node in ast.walk(tree):
		if "for" in reqs and isinstance(node, ast.For):
			# del reqs["for"]
			reqs.remove("for")
			continue
		
		if "while" in reqs and isinstance(node, ast.While):
			# del reqs["while"]
			reqs.remove("while")
			continue

		if "print" in reqs and isinstance(node, ast.Print):
			# del reqs["print"]
			reqs.remove("print")
			continue	

		if "def" in reqs and isinstance(node, ast.FunctionDef):
			# del reqs["def"]
			reqs.remove("def")
			continue

		if "if" in reqs and isinstance(node, ast.If):
			# del reqs["if"]
			reqs.remove("if")
			continue

		if "return" in reqs and isinstance(node, ast.Return):
			# del reqs["return"]
			reqs.remove("return")
			continue

	if len(reqs) == 0: 
		reqsMatch = True

	return reqsMatch, reqs

def scoreMissingReqs(missingReqs, score):
	feedback = ""
	for i in missingReqs:
		# missing = "Missing " + i + " -" + missingReqs[i] + ". " 
		missing = "Missing " + i + " -1. "
		feedback += missing
		# score -= missingReqs[i]
		score -= 1

	return score, feedback 

# TESTING CASES ==============================================

class TestCase:
	method = None
	expectedResult = None
	points = None

	def setCase(self, testCaseStr):
		caseArray = testCaseStr.split("///")
		self.method = caseArray[0]
		self.expectedResult = caseArray[1]
		self.points = int(caseArray[2])

	def appendCaseNode(self, tree):
		try:
			case = ast.parse(self.method)
		except:
			return tree 

		case = ast.parse(self.method)
		ln = tree.body[-1].lineno + 1 
		newNode = case.body[0] 
		newNode.lineno = ln 
		newNode.col_offset = 0
		ast.fix_missing_locations(newNode)

		tree.body.append(newNode)

		return tree 
		

	# True if test case passes, False otherwise 
	def runCase(self, tree):
		try:
			exec(compile(tree, filename="<ast>", mode="exec"))
		except:
			return False
		return True

	# returns if True if case passed, False other + feedback 
	def checkCase(self, tree):
		runCaseCompile = self.runCase(tree)
		if not runCaseCompile:
			feedback = self.method + " does not compile."
			return False, feedback

		# create file-like string to capture output
		codeOut = StringIO.StringIO()
		# codeErr = StringIO.StringIO()

		# capture output and errors
		sys.stdout = codeOut
		# sys.stderr = codeErr

		# exec code VERY DANGEROUS NEED TO FIND BETTER WAY!!! 
		exec(compile(tree, filename="<ast>", mode="exec"))

		# restore stdout and stderr
		sys.stdout = sys.__stdout__
		# sys.stderr = sys.__stderr__

		# s = codeErr.getvalue()

		result = codeOut.getvalue()

		codeOut.close()
		# codeErr.close()

		# add newline character to expected result
		expectedResultNL = self.expectedResult + "\n"
		if result == self.expectedResult or result == expectedResultNL: 
			feedback = self.method + " passed. "
			return True, feedback
		else:
			feedback = self.method + " did not match expected result -" + str(self.points) + "." 
			return False, feedback 

# OUTPUT TO PHP ========================================

def printResult(points, feedback):
	if points < 0:
		print 0
	else:
		print points 

	print "SCORE: " + str(points) + " " + feedback


expr = """
def goodbyes(a,b,c):
	print("Hello Worlds!")

def hello(d):
	return "hello"

"""
# code = expr 
# fxn_name = "goodbye"
# params = ['a', 'b' ]
# reqs = {"for":5, "print":2, "while":1}
# testcase = "goodbye(1,2)///Hello World!///5" 

def main(): 
	code = sys.argv[1] #student submitted code 
	reqsStr = sys.argv[2] # required strings in code 
	fxn_name = sys.argv[3]
	params = sys.argv[4]
	testcasesStr = sys.argv[5] 
	points = int(sys.argv[6])

	# points = 10
	# code = "sdgsgsd"
	# fxn_name = "goodbye"
	# params = ['a', 'b' ]
	# reqs = {"for":5, "print":2, "while":1}
	# testcasesStr = "goodbye(1,2)///Hello World!///1#goodbye(2,3)///Hello Worlds!///2"

	testcases = testcasesStr.split("#")

	feedback = ""

	# Convert reqs to dictionary 
	# reqs = createReqDict(reqsStr)
	reqs = reqsStr.split("///")

	# only get 5% if code does not compile 
	try:
		p = ast.parse(code)
	except:
		points = points - points*0.95
		feedback = "Code does not compile"
		printResult(points, feedback)
		return 1

	if "def" not in code:
		points = points - points*0.95
		feedback = "Must be a function. "
		printResult(points, feedback)
		return 1

	p = ast.parse(code)

	# Check the function name 
	funcDefMatch, funcDefNode = checkFuncDef(p, fxn_name)
	# print funcDefMatch
	if not funcDefMatch: 
		feedback += "Incorrect function name -1. "
		points = points - 1 
		p = rewriteFuncDef(p, fxn_name)
		# FuncLister().visit(p)

	# Check the parameters 
	paramTotalMatch, paramTotalDif = checkParamTotal(funcDefNode, params)
	paramNamesMatch = checkParamNames(funcDefNode, params)
	# print funcDefMatch, paramTotalMatch, paramNamesMatch 
	if not paramNamesMatch or not paramTotalMatch: 
		feedback += "Incorrect number of parameters, or incorrect parameter names -1. "
		points -= 1
		p = rewriteParams(p, params)
		# ArgLister().visit(p)

	# Check the requirements 
	reqsMatch, missingReqs = checkReqs(p, reqs)
	# print "reqs: ",reqsMatch,len(missingReqs)
	points, reqFeedback = scoreMissingReqs(missingReqs, points)
	feedback += reqFeedback

	for testcase in testcases:  
		case = TestCase()
		case.setCase(testcase)
		test = case.appendCaseNode(p)
		passed, casefeedback = case.checkCase(test) 
		feedback += casefeedback
		if not passed:
			points -= case.points

	printResult(points, feedback)

	return 0

main()