from __future__ import division
import logging

# Setting logging configs
logging.basicConfig(filename='run.log',format='%(levelname)s:%(message)s',level=logging.DEBUG)


#Global Constants, can be taken as inputs at a later time
location = "/home/adarsh/Courses/db/project/2D_Q5_ESS_REDUCTION_LS/"

# We assume uniform resolution n-dimensional plan matrix
resolution = 300

numPlans = 18
dimension = 2


cost = [ [0 for x in xrange( pow(resolution,dimension) )] for x in xrange( numPlans )]


def loadData():
	logging.info( " Loading data from files")
	for k in range(numPlans):
		file = location + str(k) + ".txt"
		logging.info( " Reading file " + file )
	
		f = open(file,'r')
		
		for j in range( pow(resolution,dimension) ):
			cost[k][j] = int(f.readline())
				
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
	
	# Check row-wise on the selected reduction dimension
	for row in range(resolution):     #fix a row
		fixRowBestPlans = []        #stores the best plan num for all the points corresponding to fixed row
		mso = 0.0
		
		for i in range( pow(resolution,dimension) ):
			loc = getCoordinatesFromIndex( i )
			if loc[d] == row:
				(p,c) = getOptimal( loc )
				fixRowBestPlans.append(p)
				
		
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
			
			if fixRowBestPlans[index] == OptPlan:  #OPTIMIZATION if OptPlan is same as fixRowBestPlans[index] subopt is 0 so skip iteration
				continue
				
			subOptCost = float(cost[bestPlanInFixedRow][i] / OptCost)
			
			if subOptCost > mso:
				mso = subOptCost
				
		logging.debug(" MSO for reducing dimension " + str(d) + " using row " + str(row) + " is " + str(mso) )
		if row == 0:
			bestRowMSO = mso
			bestRow = 0
		elif mso < bestRowMSO:
			bestRowMSO = mso
			bestRow = row
			
	return (bestRowMSO,bestRow)
	


	
	
def getCoordinatesFromIndex( index ):
	loc = []
	for x in range(dimension):
		loc.append( int(index % resolution) )
		index = index / resolution
	loc.reverse()
	return loc
	
	
## MAIN
loadData()
for i in range(dimension):
	print "Reducing dimension " + str(i)
	(msoCost, row) = dimReduceUsingRow(i)
	print "Use selectivity row " + str(row) + " with MSO " + str(msoCost)
	

'''
for i in range(resolution):

	msoCost = 0;
	msoPlan = 0;
	msolocx = 0;
	msolocy = 0;
	for j in range(resolution):
		(bestPlan,bestCost) = getOptimal(i,j)
		
		# assuming PCM holds we check from i+1 to max
		for k in range(i+1, resolution):
			(p,c) = getOptimal(k,j)
			if p == bestPlan:
				continue
			elif msoCost < ((cost[bestPlan][k][j] - p) / p):
				msoCost = (cost[bestPlan][k][j] - p) /p
				msoPlan = bestPlan
				msolocx = k
				msolocy = j
	if msoCost < bestMSO:
		bestMSO = msoCost
		bestRow = i
	print "Row " + str(i) + " MSO: " + str(msoCost) + " MSO Plan: " + str(msoPlan) + " MSO Loc(" + str(msolocx) + "," + str(msolocy) + ")"

print "Best Row for Dimension reduction: Row  " + str(bestRow) + " with MSO: " + str(bestMSO)

'''

