# python test.py String[code] String[requirements]
# will print 
# string["True" or "False" if can compile] String[score] String[feedback]

import ast 
import sys 

code = sys.argv[1] # student submitted code  
reqs = sys.argv[2] # required strings in code 

# print True if code compiles, else False
def test_parse():
	try:
		p=ast.parse(code)
	except:
		print "False" 
		return 

	print "True"

# check if requirements are in code string 
def test_reqs():
	score = 100
	feedback = ""
	reqs_array = reqs.split("///") # delimiter is ///

	# loops through each requirement, decrease score if not in code  
	for i in range(0, len(reqs_array),2): 
		req = reqs_array[i]
		if code.find(req)==-1:
			pointloss = reqs_array[i+1]
			score = score - float(pointloss)
			feedback += "Missing " + req + " -" + pointloss + "pts. "

	print score
	if feedback=="":
		print "No missing requirements."
	else:
		print feedback

test_reqs()
test_parse()