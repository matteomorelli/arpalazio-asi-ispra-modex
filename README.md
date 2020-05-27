# arpalazio-asi-ispra-modex
MoDEx, stand for model data extractor. This software is designed to help ASI SNPA project users to extract a subset of data from their model data output files using a general tool. Extracted data will be compatible with ASI ISPRA Online Visualizer https://sdati.datamb.it/asiispra-vis

## License
This project is licensed under the EUROPEAN UNION PUBLIC LICENCE v. 1.2 - see the [LICENSE.md](LICENSE) file for details

## Getting started
These instructions will get you a copy of the project up and running on your local machine. Software was tested on Centos, Ubuntu server and MacOS.
Please update pip to the latest version and use a virtual environment to wrap all your libraries.

### Prerequisites
* Python 3.6 or 3.7
* [NetCDF Operators (NCO)](http://nco.sourceforge.net/) - Version 4.6.9 or later
* [pynco](https://github.com/nco/pynco)
* [scipy](https://github.com/scipy/scipy/)
* [numpy](http://www.numpy.org/)

A virtual environment is not a prerequisite, but I strongly suggest to create and use one with the right python version. You can find installation instruction for virtualenv on [the official documentation](https://virtualenv.pypa.io/en/latest/).

All library requirements are documented in requirements.txt 
To install cd to the directory where requirements.txt is located, activate your virtualenv if you have one, run the following command:
```
pip install -r requirements.txt
```

### Installing
* Check out a clone of this repo to a location of your choice, such as
   `git clone --depth=1 https://github.com/matteomorelli/arpalazio-asi-ispra-modex.git` or make a copy of all the files including `LICENSE` files
* Copy and rename `sample.ini`, edit it accordingly to your environment

### Configuration file
This file contains location of every file needed for a successfull execution.
You must configure it accordingly to your environment.
```
[model_data]
model_indir="/path/to/your/model/data/files/"
model_type="FARM"
model_run="ROMA"
model_grid="g4"
model_timestep=5
data_prefix="arpalazio_"
data_outdir="/output/will/be/here/"

[ftp]
enabled="Y"
server="127.0.0.1"
username="ftp_username"
password="ftp_password"
remote_path="/path/to/upload/file"
```
## Usage
### Running
To start processing
```
$ python handler.py configuration_file.ini
```
Run handler.py with -h option to receive instruction
```
$ python handler.py -h
usage: handler.py [-h] [-d DATE] ini_file

positional arguments:
  ini_file              Location of configuration file

optional arguments:
  -h, --help            show this help message and exit
  -d DATE, --date DATE  Model data day YYYY/MM/DD. Default: today
```

### Log file
Log file are collected into log folder. Files are in json format compatible with datadog log management solution.

### Automation
You can schedule this software to run in an autonomous way by adding it to crontab or windows task scheduler.
Below an example of crontab scheduling to run every hour at minute 5:
```
5 * * * * /path/to/arpalazio-asi-ispra-modex/handler.py /path/to/arpalazio-asi-ispra-modex/sample.ini > /path/to/arpalazio-asi-ispra-modex/lastrun.log
```
Configure it accordingly to your needs.

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Authors

* **Matteo Morelli** - *Initial work* - [matteomorelli](https://github.com/matteomorelli)

See also the list of [contributors](https://github.com/matteomorelli/arpalazio-asi-ispra-modex/contributors) who participated in this project.

* **Andrea Bolignano** - [andrea-bolignano](https://github.com/andrea-bolignano)
