#!/usr/bin/env python

'''
---------------------------------------------------------------
@author: K. Druken- NCI (kelsey.druken@anu.edu.au)
Date Created:   20-Nov-2015
Version: 4


---------------------------------------------------------------
Non-standard Dependencies:
    Python modules: numpy, netCDF4, cdms
    Libraries: udunits

Initial setup: 
    See readme file for more detailed information. Before 
    running code for first time, the udunits2 library path 
    might need to be added on your system. The 'udunits' 
    library name may also need modification if using on OSX. 
    See the 'cfchecks.py' included in checkerfiles/ and 
    comment/uncomment appropriate line for your system.
 
--------------------------------------------------------------
'''
from checkerfiles import *



'''--------------------------------------------------------------
Main Program
--------------------------------------------------------------'''	
def main():
	
	start_time = datetime.now()

	# Make a temporary working directory
	workdir = os.path.dirname(os.path.abspath(__file__))
	tmpdir = tempfile.mkdtemp(prefix='tmp', dir=workdir)

	'''--------------------------------------------------------------
	Get user inputs, initialise queues, and determine number of 
	processes to split jobs across. 
	--------------------------------------------------------------'''
	inputs = getinputs(sys.argv)	

	# Define queues for all the data/metadata reporting
	# that need saving from each process
	run = checkfiles.check()
	
	print "Searching directory and subdirectories for '.nc' files..."
	run.getAllFiles(inputs.path, inputs.nf)


	# If number of files is less than requested 'np', reduce to np = total # files
	if inputs.ncpu > len(run.fileList):
		inputs.ncpu = len(run.fileList)


	'''--------------------------------------------------------------
	Setup, run, join, and retrieve results for output
	--------------------------------------------------------------'''	
	# Print job info
	output.begin(inputs.path, inputs.ncpu)


	try:
		# Setup a list of processes that we want to run
		print "Initiating multiprocesses..."
		processes = []
		for x in range(0, inputs.ncpu):
			p = mp.Process(target=run.worker, args=(x, tmpdir, inputs.sn))
			processes.append(p)

		# Run processes
		print "Starting multiprocesses..."
		print ""
		for p in processes:
			p.start()

		# Exit the completed processes
		for p in processes:
			p.join()
		
		print ""
		print "Joining multiprocesses..."
		print ""
		# Get process results from the output queue
		CF = [run.cf.get() for p in processes]
		META = [run.meta.get() for p in processes]
		ERR = [run.fileErr.get() for p in processes]
	
	except KeyboardInterrupt:
		for p in processes:
			p.terminate()

		print 'Removing temp files...'
		shutil.rmtree(tmpdir)
		print 'Done.'
		sys.exit('Opps something happened- ending processes, removing files, and exiting...')
	
	except:
		print "Unexpected error: ", sys.exc_info()[0], sys.exc_info()[1]
		sys.exit('Exiting.')



	# Combine the list of any files that could not be read
	fileErr = []
	for proc in range(0, inputs.ncpu):
		if ERR[proc]:
			for item in ERR[proc]:
				fileErr.append(item)

	if len(fileErr) == len(run.fileList):
		shutil.rmtree(tmpdir)
		sys.exit("NO FILES COULD BE READ. EXITING.")

	'''--------------------------------------------------------------
	Sum totals and print output
	--------------------------------------------------------------'''
	results = output.finalSum()
	for proc in range(0, inputs.ncpu):
		for attr in results.__dict__.keys():
			try:
				if attr in ['err', 'warn', 'info', 'total']:
					results.sum(attr, CF[proc].__dict__[attr])
				else:
					results.sum(attr, META[proc].__dict__[attr])
	
			except AttributeError:						
				''' 
				If the processes scan out of order or at different rates
				some will not have output to sum together, so pass.
				'''
				print 'Process: '+str(proc)+', no results from this process to sum.'
				pass


	

	'''--------------------------------------------------------------
	Calculate report scoring
	--------------------------------------------------------------'''	
	score = output.scoring()
	score.calc(results, len(run.fileList), len(fileErr))

	
	'''--------------------------------------------------------------
	Print output to report and screen
	--------------------------------------------------------------'''	
	log, inputs.fn_out = output.header(workdir, inputs.path, len(run.fileList), len(fileErr))
	output.report(results, score, log, len(run.fileList), run.filetypes)
	output.screen(inputs.fn_out)
	output.append(tmpdir, inputs.fn_out, inputs.log, inputs.ncpu, fileErr)


	'''--------------------------------------------------------------
	Cleanup and exit
	--------------------------------------------------------------'''
	# Either way, delete tmp files before exiting (unless in debug mode)
	if inputs.debug == 0:
		print 'Removing temp files...'
		shutil.rmtree(tmpdir)
		print 'Done.'
	
	# Display total duration for compliance check 
	end_time = datetime.now()
	print('Duration: {}'.format(end_time - start_time))




if __name__ == '__main__':
	main()

