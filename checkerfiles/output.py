#!/usr/bin/env python

'''
-------------------------------------------------


@author: K. Druken- NCI (kelsey.druken@anu.edu.au)
Date:   14-Aug-2015
Version: 1


-------------------------------------------------
'''

import os
lw = 90 	# line width for printed dashed lines


def begin(filesdir, file, ncpu):
	print ' '	
	print '-'*lw		
	if filesdir: 
		print 'CHECKING DIRECTORY:  ', filesdir	
	elif file:
		print 'CHECKING FILE:  ', file
	print '-'*lw	
	print ' '
	print ' '
	print 'Total PROCESSES: ', ncpu
	print ' '


def templog(cpu, ncfile):
	# Print long log version of information
	templog = open('temp'+str(cpu)+'.log', 'w')
	print >>templog, ''
	print >>templog, '-'*90
	print >>templog, 'CHECKING FILE: ', ncfile
	print >>templog, '-'*90
	print >>templog, ''
	print >>templog, ''
	print >>templog, "{:<10}{:<5}{:<60}".format('Variable', '', 'Message')
	print >>templog, "{:<10}{:<5}{:<60}".format('________', '', '_______')
	return templog


def messages(templog, var, message):
	print >>templog, "{:<10}{:<5}{:<20}".format(var, '', message)



def header(fn_out, filesdir, file, nfiles):
	import time
	
	# Print results and logfiles into one output log
	timestr = time.strftime("%Y%m%d-%H%M")
	
	# If no filename specified in inputs, then use this default format
	if not fn_out:
		fn_out = '_CFcomplianceLog_'+timestr+'.log'
	else:
		fn_out = fn_out+'_'+timestr+'.log'
	log = open(fn_out,'w')
	print >>log, '='*lw
	if filesdir:
		print >>log, 'TOP DIRECTORY:  ', filesdir
	elif file:
		print >>log, 'FILE: ', file
	print >>log, 'TOTAL FILES CHECKED = ', nfiles
	print >>log, 'DateTimeStamp: ', timestr
	print >>log, '='*lw
	print >>log, ' '
	print >>log, ' '

	return log, fn_out


def report(results, log, nfiles):
	from operator import itemgetter
	
	''' ------------------------------------
		CF-Results 
		------------------------------------''' 
	print >>log, '_'*lw
	print >>log, "{0:^90}".format("NCI CF DATA COMPLIANCE REPORT")
	print >>log, ' '
	print >>log, 'For help with data compliance, refer to the following CF and ACDD guides: \n'
	print >>log, 'http://cfconventions.org/documents.html '
	print >>log, 'http://wiki.esipfed.org/index.php/Attribute_Convention_for_Data_Discovery_1-3 '
	print >>log, ' '
	print >>log, 'To browse current list of standard variable names, refer to: \n'
	print >>log, 'http://mmisw.org/cfsn/#/ '
	print >>log, '_'*lw
	print >>log, ' '
	print >>log, '-'*lw
	print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format('CF ERRORS', '', '# issues', '', 'total files')
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.err.items(), key=itemgetter(1), reverse=True):
		print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format(key, '=', value, '/', nfiles)
	print >>log, ' '
	print >>log, ' '
	
	print >>log, '-'*lw
	print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format('CF WARNINGS', '', '# issues', '', 'total files')
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.warn.items(), key=itemgetter(1), reverse=True):
		print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format(key, '=', value, '/', nfiles)
	print >>log, ' '
	print >>log, ' '

	print >>log, '-'*lw
	print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format('CF INFO MESSAGES', '', '# issues', '', 'total files')
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.info.items(), key=itemgetter(1), reverse=True):
		print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format(key, '=', value, '/', nfiles)
	print >>log, ' '
	print >>log, ' '
	print >>log, ' '
	print >>log, ' '
	
	
	''' ------------------------------------
		Metadata-Results 
		------------------------------------''' 
	print >>log, '_'*lw
	print >>log, "{0:^90}".format("NCI ACDD METADATA COMLIANCE REPORT \n")
	print >>log, 'For help with metadata compliance, refer to the ACDD guide: \n'
	print >>log, 'http://wiki.esipfed.org/index.php/Attribute_Convention_for_Data_Discovery_1-3 '
	print >>log, '_'*lw
	print >>log, ' '
	print >>log, '-'*lw
	print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format('MISSING Required Attribute(s)', '', '# issues', '', 'total files')
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.req.items()):
		print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format(key, '=', value, '/', nfiles)
	print >>log, ' '
	print >>log, ' '
	
	''' '''
	print >>log, '-'*lw
	print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format('MISSING Highly Recommended Attribute(s)', '', '# issues', '', 'total files')
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.rec.items()):
		print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format(key, '=', value, '/', nfiles)
	print >>log, ' '
	print >>log, ' '

	''' ''' 
	print >>log, '-'*lw
	print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format('MISSING Suggested Attribute(s)', '', '# issues', '', 'total files')
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.sug.items()):
		print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format(key, '=', value, '/', nfiles)
	print >>log, ' '
	print >>log, ' '
	
	
	''' ------------------------------------
		Additional info 
		------------------------------------''' 
	print >>log, '_'*lw
	print >>log, "{0:^90}".format("FILE FORMAT & ADDITIONAL METADATA \n")
	print >>log, '_'*lw
	print >>log, ' '
	print >>log, '-'*lw
	print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format('Attribute(s)', '', '# files', '', 'total files')
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.other.items()):
		print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format(key, '=', value, '/', nfiles)
	print >>log, ' '
	print >>log, ' '
	
	print >>log, '-'*lw
	print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format('File format(s)', '', '# files', '', 'total files')
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.format.items()):
		print >>log, "{:>40}{:^5}{:^15}{:^2}{:^20}".format(key, '=', value, '/', nfiles)
	print >>log, ' '
	print >>log, ' '
	
	
	log.close()



def screen(fn_out):
	# Print results to screen output
	print ' '
	print ' '
	os.system('cat '+fn_out)



def append(fn_out, detailed_log, ncpu):
	# Append log with the raw cfchecks.py output if detailed_log == 'y' report
	log = open(fn_out,'a')
	if detailed_log == 'y':
		print >>log, '\n'*15
		print >>log, '_'*lw
		print >>log, "{0:^90}".format("Individual CF Compliance Reports")
		print >>log, ' '
		print >>log, "{0:^90}".format("CF Compliance is checked using the python code developed and maintained by NCAS Computational Modelling Services (NCAS-CMS): \n")
		print >>log, 'https://pypi.python.org/pypi/cfchecker/2.0.7 	'
		print >>log, ' '
		print >>log, '_'*lw
		log.close()
	
		for proc in range(0, ncpu):
			os.system('cat temp'+str(proc)+'.log >> '+fn_out)
		
	elif detailed_log == 'n':
		os.system('rm '+fn_out)