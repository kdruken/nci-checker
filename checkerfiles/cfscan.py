#!/usr/bin/env python

'''--------------------------------------------------------------
Scan and save the output from the NetCDF Climate Forcast 
Conventions compliance checker version 2.0.9 over each '.nc' 
file found under the specified directory. Information on 
'cfchecks.py' can be found at:

https://pypi.python.org/pypi/cfchecker/2.0.9
--------------------------------------------------------------'''	



class cf:

	def __init__(self):
		vars = ['global']
		self.err = dict.fromkeys(vars, 0)
		self.warn = dict.fromkeys(vars, 0)
		self.info = dict.fromkeys(vars, 0)
		self.total = dict.fromkeys(vars,0)
	


	def newvars(self, vars):
		for var in vars:
			if var not in self.err.keys():
				self.err[var] = 0
				self.warn[var] = 0
				self.info[var] = 0
				self.total[var] = 0




	'''
	-------------------------------------------------------
	Wrapper for CF-Convention 'cfchecks.py' 		
	-------------------------------------------------------'''
	def wrapper(self, tmplog, tmpfile):
		# Search 'cfchecks.py' output for CF errors, warnings, and info messages
		with open (tmpfile, 'r') as tmpout:
			tmpout = tmpout.read().splitlines()

		# First find variable names/indices in output
		varlist = []
		varlist.append('global')
		lnnum = [] 
		lnnum.append(0)
		strtemp = 'Checking variable: '
		for i in range(0, len(tmpout[:-3])):			
			if tmpout[i].find(strtemp) != -1:
				varlist.append(tmpout[i][len(strtemp):])
				lnnum.append(i)
		# add index for end of file	
		lnnum.append(i)	

		# Now search between variable line numbers for associated errors
		# Note: warning/error 9.5 relates to cf_role and if error/warning present, it
		# becomes associated with last known variable unless separate search is called.	
		# Has to do with how cfchecks.py is written. Including these types of errors under 
		# what's called 'global'. 

		# Update Dec-2015: going to instead sum the 'okay' number of files to be consistent
		# with the other fields in the report
		for i in range(0, len(lnnum)-1):
			print >>tmplog.fn, ' '
			currentVariable = varlist[i]
			err = warn = info = 0		
			for ltemp in tmpout[lnnum[i]:lnnum[i+1]]:
				### Checking error messages
				if ltemp.find('ERROR (9.5)') != -1:
					tmplog.message('(global)', ltemp)
					err = 1	
				elif ltemp.find('ERROR') != -1:
					tmplog.message(currentVariable, ltemp)
					err = 1

				### Checking warning messages
				elif ltemp.find('WARNING (9.5)') != -1:
					tmplog.message('(global)', ltemp)
					warn = 1
				elif ltemp.find('WARNING') != -1:
					tmplog.message(currentVariable, ltemp)
					warn = 1

				### Checking info messages
				elif ltemp.find('INFO') != -1:
					tmplog.message(currentVariable, ltemp)
					info = 1

			# If no errors, warnings or information messages found- add one count to the 
			# Total number of successful files. Either way- increase counter on total
			# occurrances for this variable.
			self.total[currentVariable] += 1
			if err == 0:
				self.err[currentVariable] += 1
			if warn == 0:
				self.warn[currentVariable] += 1
			if info == 0:
				self.info[currentVariable] += 1
				


