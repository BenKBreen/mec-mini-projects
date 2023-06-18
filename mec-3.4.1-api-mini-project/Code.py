

###### Import #### 
import json
import statistics 



###### Data ######

# Load 
Datafile = open("AFXdata.json")
Datum = json.load(Datafile)
data = Datum['dataset']['data']

# Labels for data entries
print( Datum['dataset']['column_names'] )

# 2017 data
data_2017 = [ i for i in data if int(i[0][:4]) == 2017 ]



###### Data Analysis ###### 

# Highest and lowest opening
HO = max( i[1] for i in data_2017 if i[1] != None ) 
LO = min( i[1] for i in data_2017 if i[1] != None ) 

# Largest change in one day (high vs low)
LC = max( i[2]-i[3] for i in data_2017 if i[1] != None and i[2] != None)

# Largest change across 2 days (closing price)
# Note: I'm assuming this means 2 consecutive days?
LC2D = max( abs( data_2017[i][4] - data_2017[i+1][4] ) for i in range(len(data_2017) - 1) if data_2017[i][4] != None and data_2017[i+1][4] != None)

# Average + Median Trading Volume
TV 	= [ i[6] for i in data_2017 ] 	# Trading Volume
ATV = statistics.mean(TV) 			# Average Trading Volume
MTV = statistics.median(TV) 		# Median Trading Volume
