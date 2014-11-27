import logging
import copy
import sys
#Setting Global Constants

logFile = "run.log"

location = "/home/adarsh/Courses/db/project/EAIQ8_4D_20/"

# We assume uniform resolution n-dimensional plan matrix
resolution = 20

numPlans = 324
dimension = 4

c_max = 0   #c_max in original ESS
c_min = 0       #c_min in original ESS

###### DONOT CHANGE ANYTHING AFTER THIS POINT

def loadData():
	global cost

	logging.info( " Loading data from files")
	for k in range(numPlans):
		file = location + str(k) + ".txt"
		logging.info( " Reading file " + file )
	
		f = open(file,'r')
		
		for j in range( pow(resolution,dimension) ):
			cost[k][j] = float(f.readline())
				
		f.close()
	



def getOptimal( loc ):
	bestCost = cost[0]
	bestPlan = 0
	index = getIndexForLocation( loc )
	for i in range(numPlans):
		t = cost[i][index]
		if t < bestCost:
			bestCost = t
			bestPlan = i
	return (bestPlan,bestCost)
	



def getIndexForLocation( loc ):
	index = 0
	for j in range(dimension):
		index += pow(resolution, (dimension-j-1) ) * loc[j]
	return index

	
def getOptimalForAllPoints():
	global c_max
	global c_min

	for point in range( pow(resolution,dimension) ):
		optimalCost[point] = getOptimal( getCoordinatesFromIndex( point ) )
	
	#min and max cost for all POSP plans
	budgetForPOSP = [ [sys.maxint,0] for x in range( numPlans ) ] 
	for i in range ( pow(resolution,dimension) ):
		(optPlan,optCost) = optimalCost[i]
		if 	optCost < budgetForPOSP[optPlan][0]:
			budgetForPOSP[optPlan][0] = optCost
		if optCost > budgetForPOSP[optPlan][1]:
			budgetForPOSP[optPlan][1] = optCost
	
	c_max = max( [budgetForPOSP[i][1] for i in range( numPlans )] )
	c_min = min( [budgetForPOSP[i][0] for i in range( numPlans )] )




def dimReduceUsingRow( d ):
	bestRowMSO = 0.0
	bestRow = 0
	bouquet = {}


	# Check hyperplane-wise on the reduction dimension d
	for row in range(resolution):     #fix a hyperplane
		fixRowPlans = {}  #key=reduced POSP;  value=["min cost budget", "max cost budget", "num of points where plan will execute"]
		msoMin = 0.0
		msoMax = 0.0
		minDiff = [sys.maxint,0] #[bestCost,optCost]
		maxDiff = [0,0] #[bestCost,optCost]
		
		rhoMaxReduced = 0

		#find reduced POSP - reduced POSP are all plans in the fixed hyperplane
		for i in range( pow(resolution,dimension) ):
			loc = getCoordinatesFromIndex( i )
			if loc[d] == row:
				(p,c) = optimalCost[i]
				if p in fixRowPlans.keys():
					if c < fixRowPlans[p][0]:
						fixRowPlans[p][0] = c
					elif c > fixRowPlans[p][1]:
						fixRowPlans[p][1] = c
					fixRowPlans[p][2] += 1
				else:
					fixRowPlans[p] = [c,c,1]    #min cost, max cost, num-of-points
				
		#Does FPC at all points in space and finds min and max budget for reduced POSP plans
		for i in range( pow(resolution,dimension) ):  
			loc = getCoordinatesFromIndex( i )

			if loc[d] == row:   # OPTIMIZATION donot explore for fixed hyperplane
				continue
				
			
			(optPlan,optCost) = optimalCost[i]
			
			#find (bestPlan,bestCost) for this point among the reduced POSP
			bestCost = sys.maxint
			bestPlan = 0
			for plan in fixRowPlans.keys():
				if cost[plan][i] < bestCost:
					bestCost = cost[plan][i]
					bestPlan = plan
			
				
			# check if this point cost is lesser than min budget assigned to bestPlan
			fixRowPlans[bestPlan][0] = bestCost if bestCost < fixRowPlans[bestPlan][0] else fixRowPlans[bestPlan][0]
			
			# check if this point cost is greater than max budget assigned to bestPlan
			fixRowPlans[bestPlan][1] = bestCost if bestCost > fixRowPlans[bestPlan][1] else fixRowPlans[bestPlan][1]
				
			#increment number of points at which plan will execute
			fixRowPlans[bestPlan][2] += 1		

			#find minDiff and maxDiff Cost			
			if (bestCost - optCost) < (minDiff[0] - minDiff[1]):
				minDiff = [bestCost, optCost] 
			if (bestCost - optCost) > (maxDiff[0] - minDiff[1]):
				maxDiff = [bestCost, optCost]
	
				
		#find rhoMaxReduced in reduced ESS
		c_max_reduced = max( [ fixRowPlans[i][1] for i in fixRowPlans.keys() ] )
		c_min_reduced = c_min 
		rhoMaxReduced = 0


		costi = c_min
		contour = 1
		kdashmax = -1
		kmax = -1
		kdashmin = -1
		kmin = -1
		
		while costi <= c_max_reduced:
			rho = 0
			for plan in fixRowPlans.keys():
				if ( fixRowPlans[plan][0] < costi ) and ( fixRowPlans[plan][1] > costi ):
					rho += 1
				
			rhoMaxReduced = rho if rho > rhoMaxReduced else rhoMaxReduced

			if maxDiff[0] < costi and kdashmax == -1:
				kdashmax = contour
			if maxDiff[1] < costi and kmax == -1:
				kmax = contour
			if minDiff[0] < costi and kdashmin == -1:
				kdashmin = contour
			if maxDiff[1] < costi and kmin == -1:
				kmin = contour
				
			costi *= 2					
			contour += 1


		if maxDiff[0] < costi and kdashmax == -1:
			kdashmax = contour
		if maxDiff[1] < costi and kmax == -1:
			kmax = contour
		if minDiff[0] < costi and kdashmin == -1:
			kdashmin = contour
		if maxDiff[1] < costi and kmin == -1:
			kmin = contour
			
		if dimension == 2:
			rhoMaxReduced = len(fixRowPlans.keys())
			
		msoMax = float(  4 * rhoMaxReduced * pow(2,(kdashmax - kmax)) )
		msoMin = float(  4 * rhoMaxReduced * pow(2,(kdashmin - kmin)) )
		
		logging.debug(" Reduced ESS, for dimension " + str(d) + " for row: " + str(row) + " maxMSO: " +  str(msoMax) + " minMSO: " + str(msoMin) )
		
		#find and return lowest MSO row
		if row == 0:
			bestRowMSO = msoMax
			bestRow = 0
			bouquet = copy.deepcopy(fixRowPlans)
			
		elif msoMax < bestRowMSO:
			bestRowMSO = msoMax
			bestRow = row
			bouquet = copy.deepcopy(fixRowPlans)
		
	
	# find overlap factor for all boquet plans
	# num points plan p covers due to increased budget / num points plan p is supposed to execute

	for plan,planDetails in bouquet.items():
		pointsCovered = 0
		for i in range( pow(resolution,dimension) ):
			if cost[plan][i] <= planDetails[1]:     # if budget for plan is less than cost of execution of plan at that point
				pointsCovered += 1
		bouquet[plan][2] = float( pointsCovered / planDetails[2] )  # overlap factor!

	return (bestRowMSO,bestRow,bouquet)
	

	
	
def getCoordinatesFromIndex( index ):
	loc = []
	for x in range(dimension):
		loc.append( int(index % resolution) )
		index = index / resolution
	loc.reverse()
	return loc
	

'''
#	
## MAIN
## We can use this to test sequential run of ESSReduction
#

# Setting logging configs
logging.basicConfig(filename=logFile,format='%(levelname)s:%(message)s',level=logging.DEBUG)

cost = [ [0 for x in xrange( pow(resolution,dimension) )] for x in xrange( numPlans )]
optimalCost = [[0,0] for x in xrange( pow(resolution,dimension) )]
budgetForPOSP = [ [sys.maxint,0] for x in range( numPlans ) ] 
rhoOriginal = 0

loadData()
getOptimalForAllPoints()
for i in range(dimension):
	print "Reducing dimension " + str(i)
	(msoCost, row, bouquet) = dimReduceUsingRow(i)
	print "Use selectivity row " + str(row) + " with MSO " + str(msoCost)
	print ""
	print "Plan Bouquet with budgets"
	for k,v in bouquet.iteritems():
		print str(k) + " : " + str(v)
	print "----------"
'''
