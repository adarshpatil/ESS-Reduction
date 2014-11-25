import threading
import ESSReduction as ESSR
import logging
import Queue
import sys

#Setting Global Constants

logFile = "parallel_run.log"

location = "/home/adarsh/Courses/db/project/EAIQ8_4D_20/"

# We assume uniform resolution n-dimensional plan matrix
resolution = 20

numPlans = 324
dimension = 4

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
			print "Here's the Plan Bouquet"
			print "Plan Number : Budget : Overlap Factor"
			for plan,planDetails in bouquet.items():
				print str(plan) + " : " + str(planDetails[0]) + " : " + str(planDetails[1])
			print "----------"
		
			lock.release()
			
		logging.debug(" Thread " + str(self.threadID) + " queue size remaining " + str(self.__queue.qsize()) + " GOOD BYE")
	

#
## MAIN
#

cost = [ [0 for x in xrange( pow(resolution,dimension) )] for x in xrange( numPlans )]
optimalCost = [[0,0] for x in xrange( pow(resolution,dimension) )]  #[p,c] for all points
budgetForPOSP = [ [sys.maxint,0] for x in range( numPlans ) ] #[min,max] for all plans

ESSR.cost = cost
ESSR.optimalCost = optimalCost
ESSR.budgetForPOSP = budgetForPOSP
ESSR.location = location
ESSR.resolution = resolution

ESSR.rhoMax = 0  #densest contour in Original ESS
ESSR.c_max = 0   #c_max in original ESS
ESSR.c_min = 0       #c_min in original ESS

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
ESSR.getOptimalForAllPoints()

print "Processing started.. (Refer run logs)"
print "Forking " + str(dimension) + " threads"

for i in range(numThreads):
	parallelESSReduction(dimQ, i).start()

	
dimQ.join()



	
			
		
