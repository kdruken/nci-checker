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

		#f = nc.Dataset(file, 'r')
		with nc.Dataset(file, 'r') as f:
			# Read/output netcdf format information (e.g., netCDF3, netCDF4)
			self.ncformat = f.file_format
			if self.ncformat != f.data_model:
				print "f.file_format and f.data_model inconsistent"
			
			# Read/output global attributes
			self.atts = f.ncattrs()
			
			# Read/output variables and dimensions
			self.dims = f.dimensions.keys()
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
		self.conv = {}
		self.nci = {'crs_defined': 0, 'crs_not_applicable': 0, 'coordinate_attr': 0, 'coordinate_vars_defined': 0}
	
	def acddCheck(self, ncattrs):
		for item in self.req:
			if item in ncattrs:
				self.req[item] += 1
				ncattrs.remove(item)
				
		for item in self.rec:
			if item in ncattrs:
				self.rec[item] += 1
				ncattrs.remove(item)
				
		for item in self.sug:
			if item in ncattrs:
				self.sug[item] += 1
				ncattrs.remove(item)
				
		for item in ncattrs:
			if item in self.other.keys():
				self.other[item] += 1
			else:
				self.other[item] = 1
	
	def fileFormat(self, format):
		if format in self.format.keys():
			self.format[format] += 1
		else:
			self.format[format] = 1

	def conventions(self, conv):
		if conv in self.conv.keys():
			self.conv[conv] += 1
		else:
			self.conv[conv] = 1


	def spatialCheck(self, ncvars):
		spatial = 'no'
		coordattr = 'no'
		crs = 'no'
		for variable in ncvars:
			if variable.lower() in ['lat', 'lon', 'latitude', 'longitude']:		
				spatial = 'yes'
			if 'coordinates' in variable.ncattrs():
				coordattr = 'yes'
			if variable.lower() == 'crs':
				crs = 'yes'

		# Record if crs information included or if not relevant
		if spatial == 'yes' and crs == 'yes':
			self.nci['crs_defined'] += 1
		elif spatial == 'no':
			self.nci['crs_not_applicable'] += 1

		# Record whether any variables contain the 'coordinates' attribute
		# (Note- this is only important for gridded data in the case of some
		#  tool. In particular, netcdfSubset in THREDDS.)
		if coordattr == 'yes':
			self.nci['coordinate_attr'] += 1


	def coordvarCheck(self, ncdims, ncvars):
		i = 0
		for dim in ncdims:
			if dim in ncvars:
				i += 1

		if i == len(dims):
			self.nci['coordinate_vars_defined'] += 1	
		
		

'''_____________ ACDD Metadata Dictionary _____________'''
	
def check_req():
	return [
		'title',
		'summary',
		'source',
		'date_created',
		'product_version'
		]

def check_rec():
	return [
		'Conventions',
		'metadata_link',
		'history',
		'doi',
		'institution',
		'license',
		'processing_level',
		'project',
		'instrument',
		'platform',
		]
	
def check_sug():
	return [
		'date_modified',
		'date_issued',	
		'references',
		'id',
		'keywords',
		'keywords_vocabulary',
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
		'time_coverage_resolution',
		'geospatial_bounds',
		'geospatial_bounds_crs',
		'geospatial_bounds_vertical_crs',
		'geospatial_lat_units',
		'geospatial_lon_units',
		'geospatial_vertical_units',
		'geospatial_lat_resolution',
		'geospatial_lon_resolution',
		'geospatial_vertical_resolution',
		]
