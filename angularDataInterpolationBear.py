import logging
import re
from coalib.bears.LocalBear import LocalBear




class angularJSversion(LocalBear):
    def run(self, filename, file):
    	pattern = "[a-zA-Z]+\.[a-zA-Z]" #find function usage in angular HTML view using regex (format: example.function)
    	ngpattern = "ng.[a-zA-Z]" #find correct data interpolation method ng- to compare found function line with. (format: ng-bind="example")
    	curlypattern = "{{.+[a-zA-Z0-9]}}" #find correct data interpolation method {{}} to compare found function line with (format= {{ variable }} )

	"""
	Open files given from Coala command line and look for the functions within the HTML views
	if incorrect data interpolation is found raise coala to notify user
	"""
    	with open(filename) as f:
    		for line in f:
    			if re.search(pattern, line):
    				if re.search(ngpattern, line):
    					logging.debug("Correct data interpolation found ( ng-bind used)")
    				elif re.search(curlypattern, line):
    					logging.debug("Correct data interpolation found ({{ x }} used)")
    				else:
    					yield self.new_result("Incorrect data interpolation found! use ng-bind or {{ data }} to prevent XXS vulnerabilities in your Angular app \n Found on line " + line,	file=filename )
    			else:	
    				logging.debug("no hit")