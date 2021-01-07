from email import message
import logging
import re

from coalib.bears.LocalBear import LocalBear


class PythonFunction(object):
    def __init__(self, name, start, end, segment, fname, variables):
        self.name = name
        self.start = start
        self.end = end
        self.segment = segment
        self.fname = fname
        self.variables = variables

class FunctionList(PythonFunction):
    def __init__(self):
        self.functions = {}

    def removeNextLine(self, name):
        tName = name.replace('\n','')
        return tName


    def add(self, name, start, end, file):
        """
        Adds a PythonFunction object to the funcions dict.

        :param name: line string of the function name
        :param start: start line of function
        :param end: end line of function
        """
        name = self.removeNextLine(name)

        #get function name
        fname = name.split()[1]
        fname = re.search(r"^([^(]*)", fname).group(0)
        #print(fname)
        
        # get the variables
        variables = re.search(r"\(.*?\)", name).group(0)
        variables = variables[1:-1]
        variables = variables.replace(" ","").split(",")
        #print(variables)

        segment = file[start:end-1]
        #print("adding function to list: ")
        #print(name)
        pf = PythonFunction(name,start,end,segment, fname, variables)
        self.functions[name] = pf
    
    def get(self, name):
        """
        
        Retrieves a PythonFunction object from the funcions dict.
        
        :param name: line of the function name
        
        :returns FunctionList class object of given function
        """

        name = self.removeNextLine(name)
        #print(name)
        pf = self.functions[name]
        return pf

    def checkVariables(self, name):
        """

        Returns list of all unused variables of a function

        :param name: line of the function name
        """

        pf = self.get(name)
        tempVariables = pf.variables

        for i, line in enumerate(pf.segment[1:]):
            res = [ele for ele in pf.variables if(ele in line)]
            for v in res:
                if v in pf.variables:
                    tempVariables.remove(v)
        
        #print(tempVariables)
        return tempVariables

    
    def scan(self, name, file, regex):
        """
        Scans a function with the given regex and returns if it matches something.

        :param name: line of the function name
        :param file: file where the function is in
        :param regex: regular expression

        :returns matching regular expression
        """

        pf = self.get(name)

        #print(f"{pf.start} <start - end> {pf.end}")
        
        #print(file[pf.start:pf.end-1])
        for i, line in enumerate(pf.segment):
            #print(regex)
            #print(line)
            match = re.search(regex, line)
            #if match: print(match.string)
    
    def checkCursor(self, name):

        pf = self.get(name)
        curs = {}
        for i, line in enumerate(pf.segment[1:]):
            if "cursor()" in line and "=" in line:
                line = line.replace(" ","")
                line = line.split("=")
                curs[i] = line[0]
        #print(curs)

        for v in curs:
            var = curs[v]
            exec = var+".execute("
            for i, line in enumerate(pf.segment[1:]):
                if exec in line:
                    #i+1 because code skips the first line of the code (def ...)
                    print(f"SQL query found in {pf.name} on line {pf.start+i+1}. Watch out for possible unsanitized inputs. (SQLi)")
        return curs



        

class DjangoBear(LocalBear):
    def run(self, filename, file):
        """

        Looks at a python file and returns start and ends of a function.
        """

        logging.debug("Checking file: ", filename, ".")

        functionList = FunctionList()

        def find_end(l):
            """

            Looks where a given function ends and returns the line number.

            :param i: Indent of start of function.
            :param l: Line number of start of function.

            """
            i = len(file[l]) - len(file[l].lstrip())
            #Start search at next line
            start = l+1
            #print("start indent:", i, "line:", l)

            
            
            for m, line in enumerate(file[start:], start=start):
                indent = len(line) - len(line.lstrip())
                if indent == i:
                    # m is the first line of the next function. we want the end of the current function so we go back a line.
                    # if its an empty line we go back again until the first full line.
                    m = m-1
                    while (len(file[m]) <= 1):
                        m=m-1
                    return m
            return len(file)-1 #fallback EOC

        if "views.py" in filename:

            # start and end of function variables
            start = 0
            end = 0
            for l, line in enumerate(file):
                # Check for tag
                #indent = len(line) - len(line.lstrip())

                # Register start function
                if str.lower(line).startswith("def "):
                    #print("finding end of ", line)
                    m = find_end(l)
                    #print("start:", file[l])
                    #print(m)
                    #print("end:", file[m], "\n")

                    #print("####test####")
                    #print("line: " + line)
                    #print("file[l]: " + file[l])
                    #print("file[m]: " + file[m])
                    #print("####endtest####") 
                    #print(len(file[l]))
                    functionList.add(file[l],l,m,file)

                    #check for unused variables
                    unusedVariables = functionList.checkVariables(file[l])
                    for v in unusedVariables:
                        print(f"Unused variable: {v} in function {file[l]}")
                        logging.debug(f"Unused variable: {v} in function {file[l]}")
                    
                    curs = functionList.checkCursor(file[l])

            

            #functionList.scan("def manage_tasks(request, project_id):",file,"^.")
            #for i in functionList.functions:
            #    print(i)
            #print(functionList.functions)

            yield self.new_result(message="Choose option.", file=filename)

# coala -f taskmanager/views.py -d bears -b DjangoBear -L DEBUG --flush-cache