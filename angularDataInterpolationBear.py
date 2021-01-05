import logging
import re
from coalib.bears.LocalBear import LocalBear




class angularJSversion(LocalBear):
    def run(self, filename, file):
    	pattern = "[a-zA-Z]+\.[a-zA-Z]"
    	ngpattern = "ng.[a-zA-Z]"
    	curlypattern = "{{.+[a-zA-Z0-9]}}"


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