#!/usr/bin/python

'''--------------------------------------------------------------
Check for particular standard variable name standards

** This is a modification to the CF-Convention where a new 
standard variable library can be called in order to expand 
CF-like compliance for other disciplines.
--------------------------------------------------------------'''	
def stdNameTable():
	for i in range(0, len(sys.argv)):
		# '--nci_snt' specifies to use nci version of standard name table
		if sys.argv.count('--nci_snt') == 1:
			sn = './QCchecker/Standards_Library/nci-standard-name-table.xml'
		else:
			sn = []
	return sn