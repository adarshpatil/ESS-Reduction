import threading
import ESSReduction as ESSR
import logging
import Queue

#Setting Global Constants

logFile = "parallel_run.log"

location = "/home/adarsh/Courses/db/project/2D_Q5_ESS_REDUCTION_LS/"

# We assume uniform resolution n-dimensional plan matrix
resolution = 300

numPlans = 18
dimension = 2

numThreads = dimension   #by default we inovoke as many threads as dimensions for max parallelism

###### DONOT CHANGE ANYTHING AFTER THIS POINT

class parallelESSReduction(threading.Thread):
	def __init__(self, queue, threadID):
		self.__queue = queue
		self.threadID = threadID
		threading.Thread.__init__(self)
		
	def run(self):
		while not self.__queue.empty():
			item = self.__queue.get()
			
			logging.debug(" Thread " + str(self.threadID) + " STARTING dimension reduction " + str(item) )
				
			(msoCost, row, bouquet) = ESSR.dimReduceUsingRow( item )
			
			self.__queue.task_done()
			
			logging.debug(" Thread " + str(self.threadID) + " COMPLETED dimension reduction " + str(item) )
			
			lock.acquire()  #Theards need to print our results sequentially 
			
			print "Reducing dimension " + str(i)
			print "Use selectivity row " + str(row) + " with MSO " + str(msoCost)
			print ""
			print "Plan Bouquet with budgets"
			for k,v in bouquet.iteritems():
				print str(k) + " : " + str(v)
			print "----------"
		
			lock.release()
			
		logging.debug(" Thread " + str(self.threadID) + " queue size remaining " + str(self.__queue.qsize()) + " GOOD BYE")
	

#
## MAIN
#

cost = [ [0 for x in xrange( pow(resolution,dimension) )] for x in xrange( numPlans )]

ESSR.cost = cost
ESSR.location = location
ESSR.resolution = resolution

ESSR.numPlans = numPlans
ESSR.dimension = dimension


# Setting logging configs
logging.basicConfig(filename=logFile,format='%(levelname)s:%(message)s',level=logging.DEBUG)

dimQ = Queue.Queue(dimension)
lock = threading.Lock()

# load the dimQ
for x in range(dimension):
	dimQ.put(x)
	
print "Loading data"
ESSR.loadData()

print "Processing started.. (Refer run logs)"
print "Forking " + str(dimension) + " threads"

for i in range(numThreads):
	parallelESSReduction(dimQ, i).start()

	
dimQ.join()



	
			
		
