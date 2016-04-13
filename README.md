## nci-checker 
NCI compliance checker for netCDF datasets. Checks files or directory of files against the Climate and Forecasts (CF) Convention and Attribute Convention for Dataset Discovery (ACDD). Package includes a wrapper that utilises the 'cfchecker' (https://pypi.python.org/pypi/cfchecker/2.0.9) to check for CF-compliance. 


## Usage:

  `$ python nci-checker.py [OPTIONS] [file or directory]`


  Options:

	--help 		Print this usage message and exit
	--dir 		Specifiy before directory to check entire contents
	--np 		Specifiy the number of python multiprocesses 
			to use (default np = 8)
	--log 		Save detailed output
	--brief 	Save brief summary output
	--debug		Do not delete the tmp files for debugging



## Dependencies:
- Python 2.7.x
- netCDF4
- cdms2 (part of cdat-lite)
- UDUNITS-2 package (http://www.unidata.ucar.edu/software/udunits)



## Installing on NCI's Virtual Desktop Infrastructure (VDI)
Virtual python environments are highly recommended due to the libraries that can sometimes conflict with UV-CDAT. Instructions for setting up a virtual environment with 'virtualenv' listed below. If not using a virtual environment, make sure the required dependencies are installed and skip to **"Download nci-checker"**. 


### Required VDI modules

Load the following modules (using `$ module load`): 
  - udunits
  - python/2.7.5
  - virtualenv/1.11.4-py2.7 
  - netcdf/4.3.3.1
  - hdf5/1.8.14
  - szip/2.1

**Notes**: 
- The first 2 modules are always required when running the checker while the netCDF, HDF5, and szip libraries are only needed on the initial install for the netCDF4 python package.



### Setting up a virtual environment

1. Make a directory for the virtualenv:

  `$ mkdir <directory>`


2. Create the virtualenv inside this new directory. 
   
  - `$ cd <directory> `
  - `$ virtualenv <venv>`



### Setting up dependencies inside the virtual environment

1. Activate the virtual environment:

  `$ source <directory>/<venv>/bin/activate`
  

2. Install dependencies with pip: 

  - `$ pip install numpy` (**Note**: try using '--ignore-installed' if a message about 'Requirement already statisfied' is displayed)
  - `$ pip install netcdf4`
  - `$ pip install cdat-lite` (**Note**: this package is needed for the 'cdms2' library)


3. To deactivate the virtual environment:

  `$ deactivate`


### Download **nci-checker**

1. Clone the git repository: 

  `$ git clone https://github.com/kdruken/nci-checker.git`
  
  

## Using **nci-checker** 

If using a virtual environment, first load the required modules and then activate the virtual environment. 

- `$ module load udunits` 
- `$ module load python` 
- `$ source <directory>/<venv>/bin/activate`

For convenience, these module loads and virtual environment activation can be combined into a simple shell script. For easy execution of the checker from any location, add the following alias to .sh file as well:

`alias ncichecker="<path_to_the_nci-checker_executable>/nci-checker.py"`


**To check a single file:**

`$ python nci-checker.py <file>`


**To check a directory:**

`$ python nci-checker.py --dir <directory>`


The default number of python multiprocesses is np = 8 but will automatically detect if less are needed. To specify a larger number use the ‘--np’ option followed by desired number. 


**To save reports:**

Add the `--log` or `--brief` flags. The `--log` will append the report with the CF and metadata information from each individual file scanned while `--brief` will save just the summary report. 

`$ python nci-checker.py --dir <directory> --log` 
