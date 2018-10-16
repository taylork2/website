import ast 
import sys
import StringIO
import copy #needed to deeply copy ast tree  
import os 

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
def isFunction(tree):
	for node in ast.walk(tree):
		if isinstance(node, ast.FunctionDef):
			return True
	return False 

# Wrap student's code in function def 
def wrapFuncDef(tree, fxnName):
	newNode = ast.FunctionDef(
				name = fxnName, 
				args = [], 
				body = tree.body,
				decorator_list = [])
	ast.fix_missing_locations(newNode)	

	tree.body = [newNode]

	print ast.dump(tree)	
	return tree


# Compare function Name to 
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
	testTree = None 

	def setCase(self, testCaseStr, tree):
		caseArray = testCaseStr.split("///")
		self.method = caseArray[0]
		self.expectedResult = caseArray[1]
		self.points = int(caseArray[2])

		self.testTree = copy.deepcopy(tree)

	def appendCaseNode(self):
		try:
			case = ast.parse(self.method)
		except:
			# TODO return something like about testCase sucks 
			return self.testTree 

		case = ast.parse(self.method)
		ln = self.testTree.body[-1].lineno + 1 
		newNode = case.body[0] 
		newNode.lineno = ln 
		newNode.col_offset = 0
		ast.fix_missing_locations(newNode)

		self.testTree.body.append(newNode)

		return self.testTree 
		

	# True if test case passes, False otherwise 
	def runCase(self):
		blockPrinting() 

		try:
			exec(compile(self.testTree, filename="<ast>", mode="exec"))
		except:
			enablePrinting()
			return False

		enablePrinting()
		return True

	# returns if True if case passed, False other + feedback 
	def checkCase(self):
		runCaseCompile = self.runCase()
		if not runCaseCompile:
			feedback = self.method + " does not compile. "
			return False, feedback

		# create file-like string to capture output, this blocks printing to terminal
		codeOut = StringIO.StringIO()
		# codeErr = StringIO.StringIO()

		# capture output and errors
		sys.stdout = codeOut
		# sys.stderr = codeErr

		# exec code VERY DANGEROUS NEED TO FIND BETTER WAY!!! 
		exec(compile(self.testTree, filename="<ast>", mode="exec"))

		# restore stdout and stderr
		enablePrinting()
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
		points = 0
		print 0
	else: 
		print points

	print "SCORE: " + str(points) + " " + feedback

# blocking output to terminal so it does not interfere with php
def blockPrinting():
	sys.stdout = open(os.devnull, 'w')  

# re enable output to terminal 
def enablePrinting():
	sys.stdout = sys.__stdout__

# expr = """
# def oper(a, b):
# 	if op == "+":
# 		print "hi"
# 		return "there"
# 	elif op == "-":
# 		return a-b
# 	elif op == "*":
# 		return a*b
# 	elif op == "/":
# 		return a/b 
# 	else:
# 		return -1 
# """

# expr = """
# asdf
# """
# code = expr 
# fxn_name = "goodbye"
# params = ['a', 'b' ]
# reqs = {"for":5, "print":2, "while":1}
# testcase = "goodbye(1,2)///Hello World!///5" 

def main(): 
	code = sys.argv[1] #student submitted code 
	reqsStr = sys.argv[2] # required strings in code 
	fxn_name = sys.argv[3] 
	paramsStr = sys.argv[4]
	testcasesStr = sys.argv[5] 
	points = int(sys.argv[6])

	params = paramsStr.split("///")
	# Convert reqs to dictionary 
	# reqs = createReqDict(reqsStr)
	reqs = reqsStr.split("///")

	# points = 10
	# code = expr
	# fxn_name = "operation"
	# params = ["op", 'a', 'b']
	# reqs = ["if", "return"]
	# testcasesStr = "print(operation(\"+\",1,2))///hi\nthere///1#print(operation(\"*\",10,3))///30///2#print(operation(\"/\", 4,2))///2///3"

	testcases = testcasesStr.split("#")

	feedback = ""

	# only get 5% if code does not compile 
	# codeErr = StringIO.StringIO()
	try:
		p = ast.parse(code)
	except Exception, e:
		points = points - points*0.9
		feedback += "Code does not compile due to: "  + str(e)
		printResult(points, feedback)
		return 1

	p = ast.parse(code)
	# print ast.dump(p)

	if not isFunction(p): 
		points_off = points * 0.4
		points = points - points_off
		feedback += "Must be a function -" + str(points_off) + ". "

		try: 
			wrapFuncDef(p, fxn_name)
		except Exception, e:
			print str(e)
			printResult(points, feedback)
			return 1

		# print ast.dump(p)
	

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

	# print ast.dump(p)

	# Check the requirements 
	reqsMatch, missingReqs = checkReqs(p, reqs)
	# print "reqs: ",reqsMatch,len(missingReqs)
	points, reqFeedback = scoreMissingReqs(missingReqs, points)
	feedback += reqFeedback

	for testcase in testcases:  
		case = TestCase()
		case.setCase(testcase, p)
		test = case.appendCaseNode()
		passed, casefeedback = case.checkCase() 
		feedback += casefeedback
		if not passed:
			points -= case.points

	printResult(points, feedback)

	return 0

main()