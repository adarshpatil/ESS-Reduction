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

rhoMax = 0  #densest contour in Original ESS
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
	global rhoMax
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
	
	#find rhoMax - densest contour in ESS
	costi = c_min
	while costi <= c_max:
		rho = 0
		for plan in range( numPlans ):
			if ( budgetForPOSP[plan][0] > costi ) and ( budgetForPOSP[plan][1] < costi ):
				rho += 1
				
		rhoMax = rho if rho > rhoMax else rhoMax
		costi *= 2
	
	print "Original ESS, rho: " + str(rho) + " c_max: " +  str(c_max) + " c_min " + str(c_min)
	logging.debug(" Calculating rho in Original ESS" )
	
def dimReduceUsingRow( d ):
	bestRowMSO = 0.0
	bestRow = 0
	bouquet = {}


	# Check row-wise on the reduction dimension d
	for row in range(resolution):     #fix a row
		fixRowPlans = {}  #key=reduced POSP;  value=["min cost budget", "max cost budget", "num of points where plan will execute"]
		mso = 0.0
		
		rhoMaxReduced = 0

		#find reduced POSP - reduced POSP are all plans in the fixed row
		for i in range( pow(resolution,dimension) ):
			loc = getCoordinatesFromIndex( i )
			if loc[d] == row:
				(p,c) = optimalCost[i]
				if p in fixRowPlans.keys():
					fixRowPlans[p][2] += 1
				else:
					fixRowPlans[p] = [sys.maxint,0,1]    #min cost, max cost, num-of-points
				
		#Does FPC at all points in space and finds min and max budget for reduced POSP plans
		for i in range( pow(resolution,dimension) ):   
			loc = getCoordinatesFromIndex( i )

			if loc[d] == row:   # OPTIMIZATION donot explore for fixedRow
				continue
				
			#find (bestPlan,bestCost) for this point among the reduced POSP
			bestCost = sys.maxint
			bestPlan = 0
			for plan in fixRowPlans.keys():
				if cost[plan][i] < bestCost:
					bestCost = cost[plan][i]
					bestPlan = plan
			
				
			# check if this point cost is greater than min budget assigned to bestPlan
			fixRowPlans[bestPlan][0] = bestCost if bestCost < fixRowPlans[bestPlan][0] else fixRowPlans[bestPlan][0]
			
			# check if this point cost is lesser than max budget assigned to bestPlan
			fixRowPlans[bestPlan][1] = bestCost if bestCost > fixRowPlans[bestPlan][1] else fixRowPlans[bestPlan][1]
				
			#increment number of points at which plan will execute
			fixRowPlans[bestPlan][2] += 1		
			
		
		#find rhoMax in reduced ESS
		c_max_reduced = max( [ fixRowPlans[i][1] for i in fixRowPlans.keys() ] )
		c_min_reduced = min( [ fixRowPlans[i][0] for i in fixRowPlans.keys() ] ) 
		rhoMaxReduced = 0

		if dimension == 2:
			rhoMaxReduced = 1
		else:	
			costi = c_min_reduced
			while costi <= c_max_reduced:
				rho = 0
				for plan in fixRowPlans.keys():
					if ( fixRowPlans[plan][0] < costi ) and ( fixRowPlans[plan][1] > costi ):
						rho += 1
				
				rhoMaxReduced = rho if rho > rhoMaxReduced else rhoMaxReduced
				costi *= 2		
		

		mso = float(  ( 2*rhoMaxReduced*(c_max_reduced - c_min_reduced) )  /  ( rhoMax*(c_max-c_min) )   )
		
		logging.debug(" Reduced ESS, for dimension " + str(d) + " for row: " + str(row) + " rho: " + str(rhoMaxReduced) + " c_max: " +  str(c_max_reduced) + " c_min: " + str(c_min_reduced) + " mso: " + str(mso) )
		
		#find and return lowest MSO row
		if row == 0:
			bestRowMSO = mso
			bestRow = 0
			bouquet = copy.deepcopy(fixRowPlans)
			
		elif mso < bestRowMSO:
			bestRowMSO = mso
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
