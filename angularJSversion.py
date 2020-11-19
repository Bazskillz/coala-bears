import logging

from coalib.bears.LocalBear import LocalBear

class angularJSversion(LocalBear):
    def run(self,
            filename,
            file):
            for line in file:
                if '"angularjs": ' in line:
                    logging.debug("HIT!")
                    yield self.new_result("Found angular version which is:" + line + ".", file=filename)
                else:
                    logging.debug("Checking line")
