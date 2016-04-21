#!/usr/bin/env python

import sys


'''--------------------------------------------------------------
Help/usage message
--------------------------------------------------------------'''
def help():
	''' 

	Usage: python nci-checker.py [OPTIONS] file/directory

	       (No flag required before listing a filename.) 

	Options:

	--help 		Print this usage message and exit
	--dir 		Specifiy before directory to check entire contents
	--np 		Specifiy the number of python multiprocesses 
			to use (default np = 8)
	--nf		Number (or 'all') of files to check (default = 1)
	--log 		Save detailed output including the CF information 
			(default output is a brief summary)
	--debug		Keep tmp files for debugging

	'''


'''--------------------------------------------------------------
Get user inputs
--------------------------------------------------------------'''
class getinputs(object):
	def __init__(self, argv):
		# If no inputs given, print help info and exit
		if len(argv) < 2:
			print help.__doc__	
			sys.exit()
		
		# '--help', print how to use this tool
		helpStr = ['--help']
		for item in argv:
			if item in helpStr:
				print help.__doc__
				sys.exit()		
				
		# Directory with 'nc' files to check, will be second input value
		self.path = []
		for j in range(0, len(argv)):
			# '--dir' specifies top directory to check
			if argv[j] == '--dir':
				self.path = str(argv[j + 1])

			elif '.nc' in argv[j]:
				self.path = str(argv[j])
		
		if not self.path:
			sys.exit("No directory or file given. Provide '.nc' file or use '--dir' followed by directory path.")

			
		# '--np' specifies the number of processes to run, default is np=8
		if argv.count('--np') == 1:
			self.ncpu = int(argv[argv.index('--np')+1]) 
		else:
			self.ncpu = 7
		
		# '--log' or '--brief' specifies long/short log option of output
		if argv.count('--log') == 1:
			self.log = 'y'
		elif argv.count('--brief') == 1:
			self.log = 'b'
		else:
			self.log = 'n'
			

		# '--debug': flag for debugging, leaves tmp files
		if argv.count('--debug') == 1:
			self.debug = 1
		else:	
			self.debug = 0

		
		# '--nci_snt' specifies to use nci version of standard name table
		for i in range(0, len(argv)):
			if argv.count('--nci_snt') == 1:
				# This is currently a copy of the CF standard name table but 
				# can be used to extend CF standard names in future work.
				self.sn = './checkerfiles/nci-standard-name-table.xml'
			else:
				self.sn = []

		# '-v' specifices CF-Convention version to check against 
		# (default is most recent if not specified within file)
		if argv.count('--v') == 1:
			self.cfver = int(argv[argv.index('--v')+1])
		else:
			self.cfver = 'auto'

		
		# '--nf' specifies number of files to check
		# Use if wanting to skip the prompt asking for this value.
		# To check all files found use 'all' instead of numeric value.
		if argv.count('--nf') == 1:
			if argv[argv.index('--nf')+1] == 'all':
				self.nf = 'all'
			else:
				try:
					self.nf = int(argv[argv.index('--nf')+1])
				except ValueError:
					sys.exit("Error: '--nf' value must be numeric or 'all'")
		else: 
			self.nf = []
				
