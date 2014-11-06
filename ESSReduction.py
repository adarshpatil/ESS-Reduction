import numpy

#Global Constants, can be taken as inputs at a later time
location = "/home/adarsh/Courses/db/project/2D_Q5_ESS_REDUCTION/"

# We assume uniform resolution n-dimensional plan matrix
resolution = 300

numPlans = 34
dimension = 2


cost = []	


def loadData():
	for k in range(numPlans):
		file = location + str(k) + ".txt"
		print "reading file " + file
	
		f = open(file,'r')
	
		for i in range(resolution):
			for j in range(resolution):
				cost.append( int(f.readline()) )

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
	bestMSO = 0
	bestRow = 0
	 
	for row in range(resolution):     #fix a row
		fixRowBestPlans = []        #stores the best plan num for all the points corresponding to fixed row
		mso = 0
		
		for i in range( pow(resolution,dimension) ):
			loc = getCoordinatesFromIndex( i )
			if loc[d] == row:
				(p,c) = getOptimal( loc )
				fixRowBestPlans.append(p)

		# size of fixRowBestPlans is pow( resolution, dimension-1 )
		
		for i in range( pow(resolution,dimension) ):
			loc = getCoordinatesFromIndex( i )
			(p,c) = getOptimal( loc )

			#compute index to lookup into fixRowBestPlans with n-1 dimension
			index = 0
			for x in range(dimension):
				if x == d:
					continue
				else:
					index += pow(resolution, (dimension-j-1) ) * loc[x]
			
			bestPlanInFixedRow = fixRowBestPlan[index]
			
			subOptCost = cost[bestPlanInFixedRow][i]
			if subOptCost < mso
				mso = subOptCost
				
					
		if i == 1:
			bestMSO = msoCost
			bestRow = 1
		elif msoCost < bestMSO:
			bestMSO = msoCost
			bestRow = i
			
	return (bestMSO,bestRow)
	


	
	
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
	print "Reducing dimension " + i
	(row, msoCost) = dimReduceUsingRow(i)
	print "Use selectivity row " + row + " with MSO " + msoCost
	
# Check row-wise on each iso-cost selectivity dimension
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

