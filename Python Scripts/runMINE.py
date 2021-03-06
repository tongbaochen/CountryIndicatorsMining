import os
import re
import csv
import numpy as np
from subprocess import call
from operator import add

def MINE1Year(folderPath = './New Formatted Files'):
	""" 
	Execute MINE software to investigate relationships between target variables and the others in the same year.
	Do this for all years containing each target indicator and average the results to be a summary of each target indicator.
	The results are saved into the same folder as the data files e.g. Indicator808.csv

	Parameters
	----------
	folderPath : string
		A path to the folder containing data files generated by one of the first two functions in createFileFromData.py  

	Return Value
	----------
	None

	"""
	fileList = []
	for root, dirs, files in os.walk(folderPath):    
	    for afile in files:
	    	fileList.append(afile)

	# targetList = [2704,2707,2713,2716,2718,808,811,1954]
	targetList = [1994,1997,2003,2006,2008,807,810,1953]
	yearList = [(1998,2015),(2005,2015),(2005,2015),(2005,2015),(2005,2015),(1960,2014),(1961,2014),(2002,2012)]

	# Run MINE
	# --------------------------------------------------------------------------------------
	for i in range(len(targetList)):
		for year in range(yearList[i][0],yearList[i][1]+1):
			# print str(year) + '-' + str(targetList[i]) 
			regex = re.compile("("+ str(year) +").*")
			files = [m.group(0) for l in fileList for m in [regex.search(l)] if m]
			# print files
			call(["java","-jar","MINE.jar",folderPath+"/"+files[0],str(targetList[i]+1),"cv=0.5"])

	# Combine Results
	# --------------------------------------------------------------------------------------
	for i in range(len(targetList)):
		# >>> Find all result files
		regex = re.compile(".*(mv="+str(targetList[i]+1)+").*(csv)")
		files = [m.group(0) for l in fileList for m in [regex.search(l)] if m]
		# print files
		stat = {}
		numFiles = len(files)
		indicator = ''

		# >>> Collect Results from each file
		for afile in files:
			with open(folderPath+'/'+afile, 'rb') as f:
				reader = csv.reader(f)
				for row in reader:
					if row[0] == 'X var':
						continue
					indicator = row[0]
					oldStat = stat.get(row[1], [0.0,0.0,0.0,0.0,0.0,0.0,0.0])
					measure = row[2:]
					measure.append(1.0)
					newStat = [float(x) for x in measure]
					stat[row[1]] = map(add, oldStat, newStat)
				f.close()

		# >>> Combine results (Find mean)
		rows = []
		header = ['X var','Y var','MIC (strength)','MIC-p^2 (nonlinearity)','MAS (non-monotonicity)','MEV (functionality)','MCN (complexity)','Linear regression (p)']
		rows.append(header)

		allStat = []
		for key, value in stat.iteritems():
			aRow = [indicator]
			aRow.append(key)
			val = [1.0*x/value[6] for x in value[:-1]]
			aRow.extend(val)
			allStat.append(aRow)
		allStat.sort(key=lambda x: x[2],reverse=True)
		rows.extend(allStat)
		# for i in rows:
		# 	print i

		# >>> Write file
		filename = folderPath+'/Indicator'+str(targetList[i]+1)+'.csv'
		with open(filename,'wb') as w:
			a = csv.writer(w, delimiter = ',')
			a.writerows(rows)
		w.close()

		print indicator

def MINE2Years(folderPath = './FormattedFilesWithoutMissingToNextYear'):
	""" 
	Execute MINE software to investigate relationships between others indicators and the target indicators in the next year.
	Do this for all years whose next year contains the target indicator. 

	Parameters
	----------
	folderPath : string
		A path to the folder containing data files generated by the function createFileToTheNextYearIgnoreMissingColumn in createFileFromData.py  

	Return Value
	----------
	None

	"""
	fileList = []
	for root, dirs, files in os.walk(folderPath):    
	    for afile in files:
	    	fileList.append(afile)

	# targetList = [2704,2707,2713,2716,2718,808,811,1954]
	targetList = [1994,1997,2003,2006,2008,807,810,1953]
	yearList = [(1998,2015),(2005,2015),(2005,2015),(2005,2015),(2005,2015),(1960,2014),(1961,2014),(2002,2012)]

	# Run MINE
	# --------------------------------------------------------------------------------------
	
	for afile in fileList:
		with open(folderPath+'/'+afile, 'rb') as f:
			reader = csv.reader(f)
			header = next(reader)
			regex = re.compile("....N:.*")
			nextYearID = [m.group(0) for l in header for m in [regex.search(l)] if m]
			nextYearIndicator = len(nextYearID)
			f.close()
		print (nextYearIndicator, afile, '"'+folderPath+'/'+afile+'"')
		call(["java","-jar","MINE.jar",folderPath+"/"+afile,"-pairsBetween", str(nextYearIndicator+1),"cv=0.5"])
		# break

def MINE2YearsCombineResults(folderPath = './FormattedFilesWithoutMissingToNextYear'):
	""" 
	Average the results of function MINE2Years to be a summary of each target indicator.
	The results are saved into the same folder as the input MINE results e.g. Indicator808.csv

	Parameters
	----------
	folderPath : string
		A path to the folder containing the MINE results generated from the function MINE2Years

	Return Value
	----------
	None

	"""
	fileList = []
	regex = re.compile(".*between.*(csv)")
	for root, dirs, files in os.walk(folderPath):    
	    for afile in files:
	    	if regex.search(afile):
	    		fileList.append(afile)

	targetList = [2704,2707,2713,2716,2718,808,811,1954]
	# targetList = [1994,1997,2003,2006,2008,807,810,1953]
	yearList = [(1998,2015),(2005,2015),(2005,2015),(2005,2015),(2005,2015),(1960,2014),(1961,2014),(2002,2012)]


	# Combine Results
	# --------------------------------------------------------------------------------------
	for i in range(len(targetList)):
		# >>> Find all result files
		files = [afile for afile in fileList if int(afile[0:4]) >= yearList[i][0]-1 and int(afile[0:4]) < yearList[i][1]]
		# print files
		stat = {}
		numFiles = len(files)
		indicator = ''

		# >>> Collect Results from each file
		for afile in files:
			with open(folderPath+'/'+afile, 'rb') as f:
				reader = csv.reader(f)
				for row in reader:
					if row[0] == 'X var' or not row[0].startswith(str(targetList[i]).zfill(4)+'N'):
						continue
					indicator = row[0]
					oldStat = stat.get(row[1][:row[1].rfind(' - ')], [0.0,0.0,0.0,0.0,0.0,0.0,0.0])
					measure = row[2:]
					measure.append(1.0)
					newStat = [float(x) for x in measure]
					stat[row[1][:row[1].rfind(' - ')]] = map(add, oldStat, newStat)
				f.close()

		# >>> Combine results (Find mean)
		rows = []
		header = ['X var','Y var','MIC (strength)','MIC-p^2 (nonlinearity)','MAS (non-monotonicity)','MEV (functionality)','MCN (complexity)','Linear regression (p)','Num Year Exists']
		rows.append(header)

		allStat = []
		for key, value in stat.iteritems():
			aRow = [indicator]
			aRow.append(key)
			val = [1.0*x/value[6] for x in value[:-1]]
			val.append(value[6])
			aRow.extend(val)
			allStat.append(aRow)
		allStat.sort(key=lambda x: x[2],reverse=True)
		rows.extend(allStat)
		# for i in rows:
		# 	print i

		# >>> Write file
		filename = folderPath+'/Indicator'+str(targetList[i]+1)+'.csv'
		with open(filename,'wb') as w:
			a = csv.writer(w, delimiter = ',')
			a.writerows(rows)
		w.close()

		print indicator

def separateResultsByIndicator(originalFilename, folderName, newFilePrefix):
	""" 
	This function separates the MINE result rows based on XVar and saves the separated files in .csv format.

	Parameters
	----------
	originalFilename : string
		A filename or file path of the MINE results we want to separate.

	folderName : string
		The existing folder for storing output files.

	newFilePrefix : string
		The prefix of output files. 
		The output filename is such as 'MINE-Indicator-2011-2713.csv' whose prefix is 'MINE-Indicator-2011-' and 2713 is target indicator key.

	Return Value
	----------
	None

	"""
	# f = open('2006-2013_FilteredColsNotImputed.csv,between[break=9],cv=0.5,B=n^0.6,Results.csv','rb')
	f = open(originalFilename,'rb')
	reader = csv.reader(f)
	header = next(reader)
	MINEResults = list(reader)
	category = dict()
	for row in MINEResults:
		category[row[0]] = category.get(row[0],[header])+[row]
	for key, value in category.items():
		# filename = './Feature Selection 2006-2013/MINE-Indicator'+key[0:4]+'.csv'
		filename = './'+folderName+'/'+newFilePrefix+key[0:4]+'.csv'
		with open(filename,'wb') as w:
			a = csv.writer(w, delimiter = ',')
			a.writerows(value)
		w.close()

def separateResultsByIndicatorToARFF(originalFilename, folderName, newFilePrefix):
	""" 
	This function separates the MINE result rows based on XVar and saves the separated files in .arff format to be used in Weka.

	Parameters
	----------
	originalFilename : string
		A filename or file path of the MINE results we want to separate.

	folderName : string
		The existing folder for storing output files.

	newFilePrefix : string
		The prefix of output files. 
		The output filename is such as 'MINE-Indicator-2011-2713.csv' whose prefix is 'MINE-Indicator-2011-' and 2713 is target indicator key.

	Return Value
	----------
	None

	"""
	f = open(originalFilename,'rb')
	# f = open('./2011_2016-08-23-03-22-10.csv,between[break=9],cv=0.5,B=n^0.6,Results.csv','rb')
	reader = csv.reader(f)
	header = next(reader)
	MINEResults = list(reader)
	category = dict()
	for row in MINEResults:
		thisRow = row
		thisRow[0] = "'"+thisRow[0].replace("'",";")+"'"
		thisRow[1] = "'"+thisRow[1].replace("'",";")+"'"
		category[thisRow[0]] = category.get(thisRow[0],[])+[thisRow]
	for key, value in category.items():
		filename = './'+folderName+'/'+newFilePrefix+key[1:5]+'.arff'
		with open(filename,'wb') as w:
			w.write('@relation '+newFilePrefix+key[1:5]+'\n\n')
			w.write('@attribute XVar string\n@attribute YVar string\n@attribute MIC numeric\n@attribute MIC-p2 numeric\n@attribute MAS numeric\n@attribute MEV numeric\n@attribute MCN numeric\n@attribute p numeric\n\n')
			w.write('@data\n')
			for aRow in value:
				w.write(",".join(aRow)+'\n')
		w.close()

# separateResultsByIndicatorToARFF()
separateResultsByIndicator('2011_2016-08-23-03-22-10.csv,between[break=9],cv=0.5,B=n^0.6,Results.csv', 'For Clustering', 'MINE-Indicator-2011-')