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

    def remove_next_line(self, name):
        t_name = name.replace('\n', '')
        return t_name

    def add(self, name, start, end, file):
        """
        Adds a PythonFunction object to the funcions dict.

        :param file:
        :param name: line string of the function name
        :param start: start line of function
        :param end: end line of function
        """
        name = self.remove_next_line(name)

        f_name = name.split()[1]
        f_name = re.search(r"^([^(]*)", f_name).group(0)

        variables = re.search(r"\(.*?\)", name).group(0)
        variables = variables[1:-1]
        variables = variables.replace(" ", "").split(",")

        segment = file[start:end - 1]

        pf = PythonFunction(name, start, end, segment, f_name, variables)
        self.functions[name] = pf

    def get(self, name):
        """
        Retrieves a PythonFunction object from the funcions dict.

        :param name: line of the function name
        :returns FunctionList class object of given function
        """

        name = self.remove_next_line(name)
        pf = self.functions[name]
        return pf

    def check_variables(self, name):
        """
        Returns list of all unused variables of a function

        :param name: line of the function name
        """

        pf = self.get(name)
        temp_variables = pf.variables

        for i, line in enumerate(pf.segment[1:]):
            res = [ele for ele in pf.variables if (ele in line)]
            for v in res:
                if v in pf.variables:
                    temp_variables.remove(v)

        return temp_variables

    def check_cursor(self, name):
        pf = self.get(name)
        curs = {}
        for i, line in enumerate(pf.segment[1:]):
            if "cursor()" in line and "=" in line:
                line = line.replace(" ", "")
                line = line.split("=")
                curs[pf.name] = line[0]

        for v in curs:
            var = curs[v]
            exec = var + ".execute("
            for i, line in enumerate(pf.segment[1:]):
                if exec in line:
                    print(
                        f"SQL query found in {pf.name} on line {pf.start + i + 1}. "
                        f"Watch out for possible non-sanitised inputs. (SQLi)")
        return curs


class DjanogoVulBear(LocalBear):
    def run(self, filename, file):
        """
        DjangoVulBear
        Checks your django project for common misconfigurations and vulnerable implementation.

        """

        function_list = FunctionList()

        def find_end(l):
            """

            Looks where a given function ends and returns the line number.

            :param l: Line number of start of function.
            :return file end line
            """
            i = len(file[l]) - len(file[l].lstrip())

            start = l + 1

            for m, line in enumerate(file[start:], start=start):
                indent = len(line) - len(line.lstrip())
                if indent == i:
                    m = m - 1

                    while len(file[m]) <= 1:
                        m = m - 1
                    return m
            return len(file) - 1

        # This part of the code will check for misconfigurations in the settings.py file of the django project.
        debug_misconfigurations = ["debug = true\n", "debug=true\n", "template_debug = true\n", "template_debug=true\n"]
        if "settings.py" in filename:
            # Debug option in settings.py
            for line in file:
                if str.lower(line) in debug_misconfigurations:
                    yield self.new_result(message="Are you running this django project in production?"
                                                  " If so, please disable debug options [Current settings] > " + line,
                                          file=filename)
            # CookieStorage option in settings.py
            for line in file:
                if "cookie.CookieStorage" in line:
                    yield self.new_result(message="Local message storage is enabled, CookieStorage allows malicious"
                                                  " users to read any session data, and if your SECRET_KEY is "
                                                  "compromised they can also manipulate session data. Sessions can be "
                                                  "implemented using the session module.", file=filename)
            for line in file:
                if "MD5PasswordHasher" in line:
                    yield self.new_result(message="Are you using MD5 for as a password hashing function? Please refrain"
                                                  " from using MD5 for password storage, instead use something"
                                                  " like Argon2 or BCrypt", file=filename)

        if "views.py" in filename:
            for l, line in enumerate(file):
                if str.lower(line) == "@csrf_exempt\n":
                    func = file[l+1]
                    func = func.replace("\n","")
                    msg = f"Function {func} has a csrf_exempt tag. Make sure this is not exploitable."
                    yield self.new_result(message=msg, file=filename)

            for l, line in enumerate(file):
                if str.lower(line).startswith("def "):

                    m = find_end(l)

                    function_list.add(file[l], l, m, file)

                    unused_variables = function_list.check_variables(file[l])
                    for v in unused_variables:
                        yield self.new_result(message=f"Unused variable: {v} in function {file[l]}.", file=filename)

                    curs = function_list.check_cursor(file[l])
                    for c in curs:
                        yield self.new_result(
                            message=f"Cursor found in function {c}. You are might be using a cursor for executing"
                                    f" database queries here, please check if the input you are receiving here is"
                                    f" properly sanitized, You might accomplish this by saving the inputs with"
                                    f" django's builtin ORM, this assures your inputs are properly escaped",
                            file=filename)
