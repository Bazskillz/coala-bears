import logging

from coalib.bears.LocalBear import LocalBear

class angularMakeHttpSecureBear(LocalBear):
    def run(self,
            filename,
            file):
            for line in file:
                if '"homepage": "http://'   in line:
                    logging.debug("Found HTTP:// in your code, Please make this referention HTTPS to make it more SECURE !!!")
                    yield self.new_result("Found HTTP:// in your code, Please make this referention HTTPS to make it more SECURE !!!" + line + ".", file=filename)
                elif '"url": "http://'   in line:
                    logging.debug("Found HTTP:// in your code, Please make this referention HTTPS to make it more SECURE !!!")
                    yield self.new_result("Found HTTP:// in your code, Please make this referention HTTPS to make it more SECURE !!!" + line + ".", file=filename)		 
                else:
                    logging.debug("Checking line")
