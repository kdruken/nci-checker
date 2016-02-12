## nci-checker 
NCI compliance checker for netCDF datasets. Checks files or directory of files against the Climate and Forecasts (CF) Convention and Attribute Convention for Dataset Discovery (ACDD). Package includes a wrapper that utilises the 'cfchecker' (https://pypi.python.org/pypi/cfchecker/2.0.9) to check for CF-compliance. 


## Usage:

  `$ python nci-checker.py [OPTIONS] [file or directory]`


  Options:

	--help 		Print this usage message and exit
	--dir 		Specifiy before directory to check entire contents
	--np 		  Specifiy the number of python multiprocesses 
			      to use (default np = 8)
	--log 		Save detailed output
	--brief 	Save brief summary output
	--fn 		  Specify prefix of log/brief filename (default = datetimestamp)
	--debug		Do not delete the tmp files for debugging



## Dependencies:
- Python 2.7.x
- netCDF4
- cdms2 (part of UV-CDAT)
- UDUNITS-2 package (http://www.unidata.ucar.edu/software/udunits)



## Installing on NCI's Virtual Desktop Infrastructure (VDI)
Virtual python environments are highly recommended due to the libraries that can sometimes conflict with UV-CDAT. Instructions for setting up a virtual environment with 'virtualenv' listed below. If not using a virtual environment, make sure the required dependencies are installed and skip to step #8. 

### Setting up a virtual environment

1. Load the following modules (using `$ module load`): 
  - python/2.7.5
  - virtualenv/1.11.4-py2.7 
  - netcdf/4.3.3.1
  - hdf5/1.8.14
  - szip/2.1


2. Make a directory for the virtualenv:

  `$ mkdir <directory>`


3. Create the virtualenv inside this new directory. 

  `$ cd <directory> `
  `$ virtualenv <venv>`



### Setting up dependencies inside the virtual environment

4. Load the following modules (using `$ module load`): 
  - python/2.7.5
  - netcdf/4.3.3.1
  - hdf5/1.8.14
  - szip/2.1


5. Activate the virtual environment:

  `$ source <directory>/<venv>/bin/activate`
  

6. Install dependencies with pip: 

  - `$ pip install numpy`
  - `$ pip install netcdf4`


7. To deactivate the virtual environment:

  `$ deactivate`


### Download **nci-checker**

8. Clone the git repository: 

  `$ git clone https://github.com/kdruken/nci-checker.git`
  
  

## Using **nci-checker** 

If using a virtual environment, first load the python module (`$ module load python`) and then activate (`$ source <directory>/<venv>/bin/activate`). 


**To check a single file:**

`$ python nci-checker.py <file>`


**To check a directory:**

`$ python nci-checker.py --dir <directory>`


The default number of python multiprocesses is np = 8 but will automatically detect if less are needed. To specify a larger number use the ‘--np’ option followed by desired number. To save the report, use the ‘--brief’ or ‘--log’ options. The latter will produce a full report including individual file CF-Compliance outputs. 



