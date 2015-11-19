#!/usr/bin/env python

'''
-------------------------------------------------
Metadata conventions for batch cfChecker.py

** This acts as a library of required and 
recommended metadata fields for particular 
standards/conventions specified in main 
cfChecker.py script. 


@author: K. Druken- NCI (kelsey.druken@anu.edu.au)
Date:   14-Aug-2015
Version: 1


-------------------------------------------------
'''
import sys
# For some reason netCDF4 module not loading within virtual environment on VDI 
# Way to get around this is to append sys.path with full path to module
#sys.path.append('/home/900/kad900/.local/lib/python2.7/site-packages/netCDF4-1.1.9-py2.7-linux-x86_64.egg')
import netCDF4 as nc



# 	''' Initialise counters '''
# 	req = []
# 	rec = []
# 	sug = []
# 	ok = []
	
	
# 	''' Required fields '''
# 	meta = required()
# 	for item in meta.keys():
# 		if item not in atts:
# 			req.append(item)
# 		else:
# 			ok.append(item)
# 		
# 
# 	''' Recommended fields '''
# 	meta = recommend()
# 	for item in meta.keys():
# 		if item not in atts:
# 			rec.append(item)
# 		else:
# 			ok.append(item)
# 		
# 			
# 	''' Suggested fields '''			
# 	meta = suggest()
# 	for item in meta.keys():
# 		if item not in atts:
# 			sug.append(item)
# 		else:
# 			ok.append(item)
# 		
# 			
# 	return req, rec, sug, ok

''' 

Class routine to initialise the ACDD required (req), highly 
recommended (rec), and suggested (sug) global file attributes
as well as compare to a set of .nc file attributes (ncattrs)
and record which are not present. 

'''

class meta_check():	
	
	def __init__(self):
		self.req = dict.fromkeys(check_req(), 0)
		self.rec = dict.fromkeys(check_rec(), 0)
		self.sug = dict.fromkeys(check_sug(), 0) 
		self.other = {}
		self.format = {}
	
	def acddCheck(self, ncattrs):
		for item in self.req:
			if item not in ncattrs:
				self.req[item] = self.req[item] + 1
			else:
				ncattrs.remove(item)
				
		for item in self.rec:
			if item not in ncattrs:
				self.rec[item] = self.rec[item] + 1
			else:
				ncattrs.remove(item)
				
		for item in self.sug:
			if item not in ncattrs:
				self.sug[item] = self.sug[item] + 1
			else:
				ncattrs.remove(item)
				
		for item in ncattrs:
			if item in self.other.keys():
				self.other[item] = self.other[item] + 1
			else:
				self.other[item] = 1
	
	def saveFormat(self, format):
		if format in self.format.keys():
			self.format[format] = self.format[format] + 1
		else:
			self.format[format] = 1
				
								

'''_____________ ACDD Metadata Dictionary _____________'''
	
def check_req():
	return [
		'Conventions',
		'title',
		'summary',
		'source',
		'date_created',
		'product_version'
		]

def check_rec():
	return [
		'history',
		'institution',
		'license',
		'creator_name',
		'project',
		'standard_name_vocabulary',
		'keywords',
		'processing_level',
		'metadata_link',
		'geospatial_lat_min',
		'geospatial_lon_min',
		'geospatial_vertical_min',
		'time_coverage_start'
		]
	
def check_sug():
	return [
		'date_modified',
		'date_issued',
		'creator_type',
		'contributor_name',
		'id',	
		'references',
		'geospatial_bounds',
		'geospatial_bounds_crs',
		'geospatial_bounds_vertical_crs',
		'geospatial_lat_units',
		'geospatial_lon_units',
		'geospatial_vertical_units'
		]
