#!/usr/bin/env python

'''
-------------------------------------------------


@author: K. Druken- NCI (kelsey.druken@anu.edu.au)
Date:   14-Aug-2015
Version: 1


-------------------------------------------------
'''

import sys
# For some reason netCDF4 module not loading within virtual environment on VDI 
# Way to get around this is to append sys.path with full path to module
# sys.path.append('/home/900/kad900/.local/lib/python2.7/site-packages/netCDF4-1.1.9-py2.7-linux-x86_64.egg')
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
	
	

## Notes for future modification
## 
## To read variable information:
## 		vars = f.variables.keys()		# load names of variables
## 		
##		Make test dummy loop:
##			vari = f[vars[i]]
##	
##		Then vari.XX will give you size, coords, units, long_name, etc. info