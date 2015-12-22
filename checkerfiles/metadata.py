#!/usr/bin/env python

'''
-------------------------------------------------
@author: K. Druken- NCI (kelsey.druken@anu.edu.au)

'metadata.py' is used by 'nci-checker.py' to check
all file metadata information. When checking global
attributes, the Attribute Convention for Data 
Discovery is used (ACDD). 

-------------------------------------------------
'''
import sys
import netCDF4 as nc



class meta_check():	
	''' 
	Class routine to initialise the ACDD required (req), highly 
	recommended (rec), and suggested (sug) global file attributes
	as well as compare to a set of .nc file attributes (ncattrs)
	and record which are not present. 	
	'''	

	def __init__(self):
		self.req = dict.fromkeys(check_req(), 0)
		self.rec = dict.fromkeys(check_rec(), 0)
		self.sug = dict.fromkeys(check_sug(), 0) 
		self.other = {}
		self.format = {}
	
	def acddCheck(self, ncattrs):
		for item in self.req:
			if item in ncattrs:
				self.req[item] = self.req[item] + 1
				ncattrs.remove(item)
				
		for item in self.rec:
			if item in ncattrs:
				self.rec[item] = self.rec[item] + 1
				ncattrs.remove(item)
				
		for item in self.sug:
			if item in ncattrs:
				self.sug[item] = self.sug[item] + 1
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
		'project',
		'instrument',
		'platform',
		'standard_name_vocabulary',
		'keywords',
		'processing_level',
		'metadata_link',
		'geospatial_lat_min',
		'geospatial_lon_min',
		'geospatial_lat_max',
		'geospatial_lon_max',		
		'geospatial_vertical_min',
		'geospatial_vertical_max',
		'geospatial_vertical_positive',
		'geospatial_bounds',
		'geospatial_bounds_crs',
		'geospatial_bounds_vertical_crs',
		'time_coverage_start',
		'time_coverage_end',
		'time_coverage_duration',
		'time_coverage_resolution'
		]
	
def check_sug():
	return [
		'date_modified',	
		'references',
		'geospatial_bounds',
		'geospatial_bounds_crs',
		'geospatial_bounds_vertical_crs',
		'geospatial_lat_units',
		'geospatial_lon_units',
		'geospatial_vertical_units',
		'geospatial_vertical_resolution',
		'geospatial_lat_resolution',
		'geospatial_lon_resolution',
		'keywords_vocabulary'
		]
