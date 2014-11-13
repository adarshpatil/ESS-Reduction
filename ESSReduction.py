from __future__ import division
import logging
import copy

#Setting Global Constants

logFile = "run.log"

location = "/home/mas/13/eleprdee/Documents/DBProject/input/EAIQ8_4D_20/"

# We assume uniform resolution n-dimensional plan matrix
resolution = 20

numPlans = 324
dimension = 4


###### DONOT CHANGE ANYTHING AFTER THIS POINT

def loadData():
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

	
	
	
def dimReduceUsingRow( d ):
	bestRowMSO = 0.0
	bestRow = 0
	bouquet = {}
	
	# Check row-wise on the selected reduction dimension
	for row in range(resolution):     #fix a row
		fixRowBestPlans = []        #stores the best plan num for all the points corresponding to fixed row
		budgetForBestPlans = {}     #stores the "max cost budget" needed to be given and "num of points where this plan will be execute" for each fixRowBestPlans
		mso = 0.0
		
		for i in range( pow(resolution,dimension) ):
			loc = getCoordinatesFromIndex( i )
			if loc[d] == row:
				(p,c) = getOptimal( loc )
				fixRowBestPlans.append(p)
				budgetForBestPlans[p] = [0,0]
		
		# size of fixRowBestPlans is pow( resolution, dimension-1 )
		
		
		for i in range( pow(resolution,dimension) ):   #finds MSO using plans in Fixed Row by exploring complete space
			loc = getCoordinatesFromIndex( i )
			if loc[d] == row:   # OPTIMIZATION donot explore for fixedRow
				continue
			(OptPlan,OptCost) = getOptimal( loc )
				
				
			#compute index to lookup into fixRowBestPlans with n-1 dimension
			index = 0
			p = 0
			for x in range(dimension):
				if x == d:
					continue
				else:
					index += pow(resolution, (dimension-p-2) ) * loc[x]
					p += 1	
			
			bestPlanInFixedRow = fixRowBestPlans[index]
			
			# increment "num of points where plan 'bestPlanInFixedRow' executes"
			budgetForBestPlans[bestPlanInFixedRow][1] += 1


			if bestPlanInFixedRow == OptPlan:  #OPTIMIZATION: if OptPlan = fixRowBestPlans[index] subopt, is 0 so skip iteration
				continue
			
			bestPlanInFixedRowCost = cost[bestPlanInFixedRow][i]
			subOptCost = float( bestPlanInFixedRowCost / OptCost)
			
			if bestPlanInFixedRowCost > budgetForBestPlans[bestPlanInFixedRow][0]:      #find highest cost budget
				budgetForBestPlans[bestPlanInFixedRow][0] = bestPlanInFixedRowCost
				
			if subOptCost > mso:        #find highest mso value per row
				mso = subOptCost
				
		logging.debug(" MSO for reducing dimension " + str(d) + " using row " + str(row) + " is " + str(mso) )
		
		#find and return lowest MSO row
		if row == 0:
			bestRowMSO = mso
			bestRow = 0
			bouquet = copy.deepcopy(budgetForBestPlans)
			
		elif mso < bestRowMSO:
			bestRowMSO = mso
			bestRow = row
			bouquet = copy.deepcopy(budgetForBestPlans)
		
	
	# find overlap factor for all boquet plans
	# num points plan p covers due to increased budget / num points plan p is supposed to execute

	for plan,planDetails in bouquet.items():
		pointsCovered = 0
		for i in range( pow(resolution,dimension) ):
			if cost[plan][i] <= planDetails[0]:     # if budget for plan is less than cost of execution of plan at that point
				pointsCovered += 1

		planDetails[1] = float( pointsCovered / planDetails[1] )  # overlap factor!

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

loadData()
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
