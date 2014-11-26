#!/usr/bin/python
import threading
import ESSReduction as ESSR
import logging
import Queue
import sys
import optparse

#Setting Global Constants

logFile = "parallel_run.log"

# These are now passed as arguments
#location = "/storage/hpc/homes/adarsh/dbproject/EAIQ5_3D_20/"

# We assume uniform resolution n-dimensional plan matrix
#resolution = 20

#numPlans = 50
#dimension = 3

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
			
			print "Reducing dimension " + str(item)
			print "Use selectivity row " + str(row) + " with MSO " + str(msoCost)
			print ""
			print "Here's the Plan Bouquet"
			print "Plan Number : Budget : Overlap Factor"
			for plan,planDetails in bouquet.items():
				print str(plan) + " : " + str(planDetails[1]) + " : " + str(planDetails[2])
			print "----------"
		
			lock.release()
			
		logging.debug(" Thread " + str(self.threadID) + " queue size remaining " + str(self.__queue.qsize()) + " GOOD BYE")
	

#
## MAIN
#

parser = optparse.OptionParser()
parser.add_option("-l", "--location", dest="location", action="store",
                  help="absolute path of directory containing cost of plans at all points")
parser.add_option("-r", "--resolution", dest="resolution", action="store",
                  help="resolution of space")
parser.add_option("-n", "--numPlans", dest="numPlans", action="store",
                  help="number of plans")
parser.add_option("-d", "--dimension", dest="dimension", action="store",
                  help="number of dimensions")

options, args = parser.parse_args()

numPlans = int(options.numPlans)
location = options.location
dimension = int(options.dimension)
resolution = int(options.resolution)


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
numThreads = dimension   #by default we inovoke as many threads as dimensions for max parallelism


# Setting logging configs
logging.basicConfig(filename=logFile,format='%(levelname)s:%(message)s',level=logging.DEBUG)

dimQ = Queue.Queue(dimension)
lock = threading.Lock()

# load the dimQ
for x in range(dimension):
	dimQ.put(x)
	
logging.info(" Running for INPUT: " + location)
print "Loading data"
ESSR.loadData()
ESSR.getOptimalForAllPoints()

print "Processing started.. (Refer run logs)"
print "Forking " + str(dimension) + " threads"

for i in range(numThreads):
	parallelESSReduction(dimQ, i).start()

	
dimQ.join()



	
			
		
