#!/usr/bin/env python

'''
-------------------------------------------------
@author: K. Druken- NCI (kelsey.druken@anu.edu.au)

'readfile.py' uses the netCDF4 python module to 
read and extract information from the .nc file. 
Outputs to 'nci-checker.py' the global attributes,
netcdf file format, and the variable names. 
-------------------------------------------------
'''

import sys
import netCDF4 as nc


class read(object):

	def __init__(self, file):

		f = nc.Dataset(file, 'r')
		
		# Read/output netcdf format information (e.g., netCDF3, netCDF4)
		self.ncformat = f.file_format
		if self.ncformat != f.data_model:
			print "f.file_format and f.data_model inconsistent"
		
		# Read/output global attributes
		self.atts = f.ncattrs()
		
		# Read/output variables
		self.vars = f.variables.keys()
		# g.groups['obs'].variables.keys()		# Not to self for future group modification

		# Read/output any conventions used (if any)
		if 'Conventions' in f.ncattrs():
			self.conv = f.Conventions
		elif 'conventions' in f.ncattrs():
			self.conv = f.conventions
		elif 'Convention' in f.ncattrs():
			self.conv = f.Convention
		else:
			self.conv = '(No Conventions Used)'


		#return atts, ncformat, conv, vars

