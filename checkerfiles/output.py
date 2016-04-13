#!/usr/bin/env python

'''
-------------------------------------------------
@author: K. Druken- NCI (kelsey.druken@anu.edu.au


Prints all output from 'nci-checker.py'
-------------------------------------------------
'''

import os
lw = 90 	# line width for printed dashed lines



'''--------------------------------------------------------------
Print job info
--------------------------------------------------------------'''
def begin(path, ncpu):
	print ' '	
	print '-'*lw		
	if os.path.isdir(path): 
		print 'CHECKING DIRECTORY:  ', path	
	else:
		print 'CHECKING FILE:  ', path
	print '-'*lw	
	print ' '
	print ' '
	print 'Total PROCESSES: ', ncpu
	print ' '


'''--------------------------------------------------------------
Used for the tmp logs called by cfwrapper.py
--------------------------------------------------------------'''
class tmplog:
	def __init__(self, cpu, tmpdir):
		self.fn = open(tmpdir+'/tmp'+str(cpu)+'.log', 'w')
		
	
	def header(self, ncfile):
		print >> self.fn, ''
		print >> self.fn, '-'*90
		print >> self.fn, 'CHECKING FILE: ', ncfile
		print >> self.fn, '-'*90
		print >> self.fn, ''
		print >> self.fn, ''


	def message(self, var, message):
		print >> self.fn, "{:<10}{:<5}{:<20}".format(var, '', message)

	
	def meta(self, gatts, ncformat, conv):
		print >> self.fn, "NETCDF FILE FORMAT: \t", ncformat, '\n'
		print >> self.fn, "CONVENTIONS (if any): ", conv, '\n'
		print >> self.fn, "GLOBAL ATTRIBUTES:", 
		for item in gatts:
			print >> self.fn, item, ', ', 
		print >> self.fn, '\n'
		print >> self.fn, "CF-CONVENTION OUTPUT: "


'''--------------------------------------------------------------
Print the report header
--------------------------------------------------------------'''
def header(workdir, path, nfiles, nfilesErr):
	import time
	
	# Print results and logfiles into one output log
	timestr = time.strftime("%Y-%m-%d-%H%M%S")
	
	# Output log 
	if os.path.isdir(path):
		name = path.split("/")
		fn_out = workdir+'/NCI-QC-Report_'+name[3]+'_'+name[-2]+'_'+timestr+'.log'
	else:
		fn_out = workdir+'/NCI-QC-Report_'+timestr+'.log'

	log = open(fn_out,'w')
	print >>log, '='*lw
	if os.path.isdir(path):
		print >>log, 'TOP DIRECTORY:  ', path
	else:
		print >>log, 'FILE: ', path
	print >>log, 'TOTAL FILES CHECKED = ', nfiles
	print >>log, 'TOTAL FILES SKIPPED = ', nfilesErr
	print >>log, 'DateTimeStamp: ', timestr
	print >>log, '='*lw
	print >>log, ' '
	print >>log, ' '

	return log, fn_out




'''--------------------------------------------------------------
Use to sum final totals 
--------------------------------------------------------------'''
class finalSum(object):
	def __init__(self):
		self.err = {}
		self.warn = {}
		self.info = {}
		self.req = {}
		self.rec = {}
		self.sug = {}
		self.other = {}
		self.format = {}
		self.conv = {}
		self.total = {}
		self.nci = {}
		
	def sum(self, attr, dict2):
		dict1 = self.__dict__[attr]
		for item in dict2.keys():
			if item in dict1.keys():
				dict1[item] = dict1[item] + dict2[item]
			else:
				dict1[item] = dict2[item]
		self.__dict__[attr] = dict1



'''--------------------------------------------------------------
To calculate report score 
--------------------------------------------------------------'''	
class scoring():
	def __init__(self):
		self.err = 0
		self.warn = 0
		self.info = 0
		self.req = 0
		self.rec = 0
		self.sug = 0
		self.other = 0
		self.format = 0
		self.conv = 0
		self.nci = 0

 	
	def calc(self, result, nfiles, nskip):
		cflist = ['err', 'warn', 'info']
		for attr, score in self.__dict__.items():
			for key, item in result.__dict__[attr].items():	
				if attr in cflist:
					try:
						score += float(item)/result.__dict__['total'][key]
					
					except ZeroDivisionError:
						score = 0
						
				elif key != 'total':
					score += float(item)/nfiles
		
			try:
				self.__dict__[attr] = score/len(result.__dict__[attr])

			except ZeroDivisionError:
				''' Dataset may not contain additional metadata '''
				print "Zero division error: Empty '", attr, "' dictionary"
				self.__dict__[attr] = 'n/a'


	

'''--------------------------------------------------------------
 Print the results
--------------------------------------------------------------'''
def report(results, score, log, nfiles, filetypes):
	from operator import itemgetter
	
	'''
	----------------------------
	Determine max column width 
	----------------------------'''
	dum = []
	for item in results.err.keys():
		dum.append(item)

	for item in results.other.keys():
		dum.append(item)

	maxwidth = max(len(item) for item in dum)

	if maxwidth > 40:
		cw = maxwidth
		lw = maxwidth + 50
	else:
		cw = 40
		lw = 90


	'''
	----------------------------
	Main Header
	----------------------------'''
	print >>log, '_'*lw
	print >>log, "{:^{n}}".format("NCI CF DATA COMPLIANCE REPORT", n=lw)
	print >>log, ' '
	print >>log, 'For help with data compliance, refer to the following Climate and Forecasts (CF) and '
	print >>log, 'Attribute Convention for Data Discovery (ACDD) guides: \n'
	print >>log, 'http://cfconventions.org/documents.html '
	print >>log, 'http://wiki.esipfed.org/index.php/Attribute_Convention_for_Data_Discovery_1-3 '
	print >>log, ' '
	print >>log, 'To browse current list of standard variable names, refer to: \n'
	print >>log, 'http://mmisw.org/cfsn/#/ '
	print >>log, '_'*lw
	print >>log, ' '




	'''
	----------------------------
	Scoring 
	----------------------------'''
	print >>log, ''
	print >>log, "{:^{n}}".format("SCORING (%)", n=lw)
	print >>log,  '_'*lw
	print >>log,  ''
	print >>log,  "{:>30}{:^20}{:^20}{:^20}".format('', 'CF', 'ACDD', 'Completeness')
	print >>log,  '_'*lw
	print >>log,  "{:>30}{:^20.0%}{:^20.0%}{:^20}".format('Required', score.err, score.req, '--')
	print >>log,  ''
	print >>log,  "{:>30}{:^20.0%}{:^20.0%}{:^20}".format('High-priority', score.warn, score.rec, '--')
	print >>log,  "{:>30}{:^20.0%}{:^20.0%}{:^20}".format('Low-priority', score.info, score.sug, '--')
	print >>log,  ''
	
	# Might not be additional metadata ('n/a'), format accordingly
	if type(score.other) == str:
		print >>log,  "{:>30}{:^20}{:^20}{:^20}".format('Additional metadata', '--', '--', score.other)	
	else:
		print >>log,  "{:>30}{:^20}{:^20}{:^20.0%}".format('Additional metadata', '--', '--', score.other)
	print >>log,  "{:>30}{:^20}{:^20}{:^20.0%}".format('File format', '--', '--', score.format)
	print >>log,  "{:>30}{:^20}{:^20}{:^20.0%}".format('Conventions', '--', '--', score.conv)
	print >>log,  ''
	print >>log,  ''
	print >>log,  ''
	print >>log,  ''




	''' 
	------------------------------------
	CF-Results 
	------------------------------------''' 
	print >>log, '-'*lw
	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('CF-Convention (Required)', '', '# Passed', '', 'Total files', 'Score', n=cw)
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.err.items(), key=itemgetter(1,0), reverse=False):
		if results.total[key] == 0:
			score = 0
		else:
			score = float(value)/results.total[key]
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', results.total[key], score, n=cw)
	print >>log, ' '
	print >>log, ' '
	
	print >>log, '-'*lw
	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('CF-Convention (High-Priority)', '', '# Passed', '', 'Total files', 'Score', n=cw)
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.warn.items(), key=itemgetter(1,0), reverse=False):
		if results.total[key] == 0:
			score = 0
		else:
			score = float(value)/results.total[key]
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', results.total[key], score, n=cw)
	print >>log, ' '
	print >>log, ' '

	print >>log, '-'*lw
	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('CF-Convention (Low-Priority)', '', '# Passed', '', 'Total files', 'Score', n=cw)
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.info.items(), key=itemgetter(1,0), reverse=False):
		if results.total[key] == 0:
			score = 0
		else:
			score = float(value)/results.total[key]
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', results.total[key], score, n=cw)
	print >>log, ' '
	print >>log, ' '
	print >>log, ' '
	print >>log, ' '
	
	
	''' 
	------------------------------------
	Metadata-Results 
	------------------------------------''' 
	print >>log, ' '
	print >>log, '-'*lw
	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('ACDD Convention (Required)', '', '# Passed', '', 'Total files', 'Score', n=cw)
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.req.items(), key=itemgetter(1,0), reverse=False):
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', nfiles, float(value)/nfiles, n=cw)
	print >>log, ' '
	print >>log, ' '
	
	''' '''
	print >>log, '-'*lw
	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('ACDD Convention (High-Priority)', '', '# Passed', '', 'Total files', 'Score', n=cw)
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.rec.items(), key=itemgetter(1,0), reverse=False):
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', nfiles, float(value)/nfiles, n=cw)
	print >>log, ' '
	print >>log, ' '

	''' ''' 
	print >>log, '-'*lw
	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('ACDD Convention (Low-Priority)', '', '# Passed', '', 'Total files', 'Score', n=cw)
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.sug.items(), key=itemgetter(1,0), reverse=False):
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', nfiles, float(value)/nfiles, n=cw)
	print >>log, ' '
	print >>log, ' '
	
	
	''' 
	------------------------------------
	Additional info 
	------------------------------------''' 
	print >>log, '_'*lw
	print >>log, "{:^{n}}".format("ADDITIONAL GLOBAL METADATA \n", n=lw)
	print >>log, "The following sections are intended to help highlight the completeness of the additional"
	print >>log, "information included within the scanned files."
	print >>log, '_'*lw
	print >>log, ' '
	print >>log, '-'*lw
	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('Attribute(s)', '', '# Files', '', 'Total files', 'Score', n=cw)
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.other.items(), key=itemgetter(1,0), reverse=False):
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', nfiles, float(value)/nfiles, n=cw)
	print >>log, ' '
	print >>log, ' '
	
	print >>log, '-'*lw
	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('File format(s)/Conventions', '', '# Files', '', 'Total files', 'Score', n=cw)
	print >>log, '-'*lw
	print >>log, ' '
	for key, value in sorted(results.format.items(), key=itemgetter(1,0), reverse=False):
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', nfiles, float(value)/nfiles, n=cw)

	print >>log, ' '
	for key, value in sorted(results.conv.items(), key=itemgetter(1,0), reverse=False):
		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', nfiles, float(value)/nfiles, n=cw)
	print >>log, ' '
	print >>log, ' '


        # Filetypes
        print >>log, '-'*lw
        print >>log, "{:>{n}}{:^5}{:>15}{:^2}{:>15}{:^15}".format('File Types Overview', '', '# Files', '', 'Capacity (Gb)', '', '', n=cw)
        print >>log, '-'*lw
        print >>log, ' '
        for key, value in sorted(filetypes.items(), key=itemgetter(1), reverse=True):
                print >>log, "{:>{n}}{:^5}{:>15}{:^2}{:>12.1f}{:^15}".format(key, '=', value['count'], '', value['size']/1e9, '', n=cw)

        print >>log, ' '


#        # Additional NCI-specific info for spatial info and reminders for other services checks
#	print >>log, '-'*lw
#	print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15}".format('Additional checks', '', '# Files', '', 'Total files', 'Score', n=cw)
#	print >>log, '-'*lw
#	print >>log, ' '
#	for key, value in sorted(results.nci.items(), key=itemgetter(1,0), reverse=False):
#		print >>log, "{:>{n}}{:^5}{:^15}{:^2}{:^15}{:^15.0%}".format(key, '=', value, '/', nfiles, float(value)/nfiles, n=cw)

	
	log.close()



def screen(fn_out):
	# Print results to screen output
	print ' '
	print ' '
	os.system('cat '+fn_out)

	# Reprint scoring at end for easy viewing (lines 20-38)
	print ''
	os.system('sed -n 21,39p '+fn_out)
	


'''--------------------------------------------------------------
Append the output file with the cfchecks.py output (details
the CF compliance messages per file) 
--------------------------------------------------------------'''
def append(tmpdir, fn_out, detailed_log, ncpu, fileErr):

	# Append log with the raw cfchecks.py output if detailed_log == 'y' report
	if detailed_log == 'y':
		log = open(fn_out,'a')	
		print >>log, '\n'*15
		print >>log, '_'*lw
		print >>log, "{:^{n}}".format("Individual CF Compliance Reports", n=lw)
		print >>log, ' '
		print >>log, "{:^{n}}".format("CF Compliance is checked using the python code developed and maintained by NCAS Computational Modelling Services (NCAS-CMS): \n", n=lw)
		print >>log, 'https://pypi.python.org/pypi/cfchecker/2.0.7 	'
		print >>log, ' '
		print >>log, '_'*lw
		log.close()
	
		for proc in range(0, ncpu):
			os.system('cat '+tmpdir+'/tmp'+str(proc)+'.log >> '+fn_out)
	


	# Print skipped files regardless of report type
	log = open(fn_out,'a')
	print >>log, "-"*lw
	print >>log, "SKIPPED FILES: \n"	
	for file in fileErr:
		print >>log, file

	

	if detailed_log == 'n':
		os.system('rm '+fn_out)
