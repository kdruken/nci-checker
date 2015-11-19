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


def read(file):
	f = nc.Dataset(file, 'r')
	
	# Read/output netcdf format information (e.g., netCDF3, netCDF4)
	ncformat = f.file_format
	if ncformat != f.data_model:
		print "f.file_format and f.data_model inconsistent"
	
	# Read/output global attributes
	atts = f.ncattrs()
	
	# Read/output variables
	vars = f.variables.keys()
	# g.groups['obs'].variables.keys()		# Not to self for future group modification
	
	return atts, ncformat, vars

