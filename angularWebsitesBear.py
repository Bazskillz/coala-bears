import logging

from coalib.bears.LocalBear import LocalBear

class angularWebsiteBear(LocalBear):
    def run(self,
            filename,
            file):
            for line in file:
                if '"homepage":'   in line:
                    logging.debug("Found URL!")
                    yield self.new_result("Found URL`s in CODE:" + line + ".", file=filename)
                elif '"url":'   in line:
                    logging.debug("Found URL!")
                    yield self.new_result("Found URL`s in CODE:" + line + ".", file=filename)		 
                else:
                    logging.debug("Checking line")
 		
