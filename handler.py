# Copyright (c) 2020 ARPA Lazio <craria@arpalazio.it>
# SPDX-License-Identifier: EUPL-1.2

# Author: Matteo Morelli <matteo.morelli@gmail.com>

import logging
import logging.config
import traceback
import argparse
import configparser
import datetime
import sys
import json
from nco import Nco
from nco import NCOException
from libs import utils_os
from libs import utils
from libs import utils_ftp

# Script version
VERSION = "1.0.2"

# Initialize logger configuration
logging.config.fileConfig(
    'ini/logging.ini',
    disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Costant declaration
# Allowed timestep range
MIN_TIMESTEP = 1
MAX_TIMESTEP = 10

# File log handler from logginf.ini
LOG_FILE = "log/handler.log"

# FARM model basic step suffix
# TODO: integrate into a class
FARM_STEP = [
    "+000-023",
    "+024-047",
    "+048-071",
    "+072-095",
    "+096-119"]

# Service default metadata loaded from configuration file
config = utils_os.read_local_json('ini/config.json')
metadata = {
    "metadata": {
        "time": None,
        "service": config["service_name"],
        "run_name": None,
        "model_name": None,
        "grid_name": None,
        "type": config["type"]["run"],
        "subtype": config["subtype"]["man"],
        "status": config["status"]["fail"]
    }
}


def _define_check_args(parser):
    ##############################################
    # This function parse argument variable, check format
    # and set default value.
    # Arguments:
    #   a parser from argparse module
    # Returns:
    #   a tuple
    ##############################################
    parser.add_argument("ini_file", help="Location of configuration file")
    parser.add_argument("-d", "--date",
                        help="Model data day YYYY/MM/DD. Default: today")
    parser.add_argument("-a", "--auto", default=False, action='store_true',
                        help="Set run flag to AUTO.")
    args = parser.parse_args()
    # initialize variable
    day = args.date
    auto_run = args.auto

    # Set optional value to default
    if day is None:
        day = datetime.datetime.strftime(
            datetime.datetime.now(), '%Y/%m/%d')

    args_value = {
        "ini_file": args.ini_file,
        "day": day,
        "auto_run": auto_run
    }
    return args_value


def _parse_configuration_value(ini_path):
    cfg = configparser.SafeConfigParser()
    try:
        logger.info("Reading INI file: %s", ini_path)
        cfg.read(ini_path)
        logger.debug("Parsing INI values...")
        # Build dict from configuration file
        model_data = {
            'indir': cfg.get("model_data", "indir").strip("\""),
            'type': cfg.get("model_data", "type").strip("\""),
            'run': cfg.get("model_data", "run").strip("\""),
            'grid': cfg.get("model_data", "grid").strip("\""),
            'timestep': cfg.get("model_data", "timestep").strip("\""),
            'out_prefix': cfg.get("model_data", "out_prefix").strip("\""),
            'out_dir': cfg.get("model_data", "out_dir").strip("\""),
            'out_value': cfg.get("model_data", "out_value").strip("\"")
        }
        ftp_ini = {
            'enabled': cfg.get("ftp", "enabled").strip("\"").lower(),
            'server': cfg.get("ftp", "server").strip("\""),
            'username': cfg.get("ftp", "username").strip("\""),
            'password': cfg.get("ftp", "password").strip("\""),
            'remote_path': cfg.get("ftp", "remote_path").strip("\"")
        }

    except configparser.NoOptionError as err:
        logger.error("Missing option in INI file: %s", err)
        sys.exit(1)
    except configparser.ParsingError as err:
        logger.error("Error parsing INI file: %s", err)
        sys.exit(1)
    except configparser.NoSectionError as err:
        logger.error("Missing section in INI file: %s", err)
        sys.exit(1)
    except Exception:
        logger.error("uncaught exception: %s", traceback.format_exc())
        sys.exit(1)

    logger.debug("All INI values acquired")
    config = {
        "model_data": model_data,
        "ftp_ini": ftp_ini
    }
    # Empty value are not allowed
    if utils.empty_value_in_dict(config):
        logger.error("There is an empty parameter in INI file")
        sys.exit(1)
    return config


def _build_ymd_day(day_with_slashes):
    year, month, day = day_with_slashes.split("/")
    return year + month + day


def _run_type(auto_run):
    ##############################################
    # This function evaluate a boolean variable to
    # return a fixed string.
    # Arguments:
    #   boolean value based on autorun inpunt variable
    # Returns:
    #   string default value from configuration file
    ##############################################
    if auto_run:
        return config["subtype"]["auto"]
    return config["subtype"]["man"]


def _daily_autorun_check(
        log_file,
        run_name,
        model_name,
        grid_name,
        run_date_ymd):
    ##############################################
    # This function parse log file handler looking for an
    # automated successfull run, if found return true
    # Arguments:
    #   log file handlers path
    #   run name from config file
    #   run date from command line
    # Returns:
    #   bool
    ##############################################
    run_handler = open(log_file)
    for line in run_handler:
        log_line = json.loads(line)
        # look for metadata
        if "metadata" in log_line:
            # look for perfect match
            log_meta = log_line["metadata"]
            if log_meta["time"] == run_date_ymd and \
                    log_meta["service"] == config["service_name"] and \
                    log_meta["run_name"] == run_name and \
                    log_meta["model_name"] == model_name and \
                    log_meta["grid_name"] == grid_name and \
                    log_meta["type"] == config["type"]["run"] and \
                    log_meta["subtype"] == config["subtype"]["auto"] and \
                    log_meta["status"] == config["status"]["done"]:
                return True
    return False


def main():
    # Initialize value
    day = None
    conf_file = None
    auto_run = False
    # Initialize argument parser
    parser = argparse.ArgumentParser()
    in_value = _define_check_args(parser)
    logger.debug("Passed arguments: %s", in_value)
    # Starting input validation
    logger.debug("Input day: %s", in_value["day"])
    if utils.validate_input_time(in_value["day"], "d"):
        day = _build_ymd_day(in_value["day"])
    if utils_os.simple_file_read(in_value["ini_file"]):
        conf_file = _parse_configuration_value(in_value["ini_file"])
    if day is None or conf_file is None:
        logger.error("sys.exiting with error, check you logs", extra=metadata)
        sys.exit(1)
    auto_run = in_value["auto_run"]
    # Update metadata
    metadata["metadata"]["time"] = day
    metadata["metadata"]["subtype"] = _run_type(auto_run)
    metadata["metadata"]["run_name"] = conf_file["model_data"]["run"]
    metadata["metadata"]["model_name"] = conf_file["model_data"]["type"]
    metadata["metadata"]["grid_name"] = conf_file["model_data"]["grid"]
    logger.debug("Configuration values: %s", conf_file)
    # Check timestep validity
    try:
        timestep = int(conf_file["model_data"]["timestep"])
        if not MIN_TIMESTEP <= timestep <= MAX_TIMESTEP:
            logger.error(
                "Timestep is out of allowed value %s <= timestep <= %s",
                MIN_TIMESTEP,
                MAX_TIMESTEP,
                extra=metadata)
            sys.exit(1)
    except ValueError:
        logger.error("Given timestep is not a valid number", extra=metadata)
        sys.exit(1)
    # Check for automated run
    logger.debug("Automated run: %s", auto_run)
    if auto_run:
        auto_check = _daily_autorun_check(
            LOG_FILE,
            conf_file["model_data"]["run"],
            conf_file["model_data"]["type"],
            conf_file["model_data"]["grid"],
            day)
        logger.info("Looking for automated daily execution: %s", auto_check)
        if auto_check:
            logger.info("Automated run already done.", extra=metadata)
            sys.exit(0)
    # logger.info("test", extra=metadata)
    # exit()

    # Compose input filename based on model type and ini options
    # Build simple FARM concentration filename, just for crude operation
    # TODO: Write a class capable of handling input from various AQ model
    model_file = []
    for step in range(timestep):
        farm_file = (conf_file["model_data"]["type"], "_conc_",
                     conf_file["model_data"]["grid"], "_",
                     day, FARM_STEP[step], ".nc")
        model_file.append(''.join(farm_file))

    logger.info("Checking model data existence")
    if utils.is_empty(model_file):
        logger.error("Invalid filename list", extra=metadata)
        sys.exit(1)
    # ncks runtime option
    ncks_var = '-v ' + conf_file["model_data"]["out_value"]
    ncks_opt = [
        '--no-abc',
        '-O',
        ncks_var
    ]
    # check input file existence and
    # extract model data with nco operator (ncks)
    nco = Nco()
    ftp_file_list = []
    for file_name in model_file:
        in_filename = conf_file["model_data"]["indir"] + file_name
        if not utils_os.is_valid_path(in_filename, "file"):
            logger.error("%s does not exist", in_filename, extra=metadata)
            sys.exit(1)

        out_filename = conf_file["model_data"]["out_dir"] + \
            conf_file["model_data"]["out_prefix"] + \
            file_name
        # check output directory existence
        if not utils_os.is_valid_path(
                conf_file["model_data"]["out_dir"], "dir"):
            logger.error(
                "Directory %s does not exist",
                conf_file["model_data"]["out_dir"],
                extra=metadata)
            sys.exit(1)
        try:
            logger.info("Parsing file: %s", in_filename)
            nco.ncks(input=in_filename, output=out_filename, options=ncks_opt)
            # if ftp transmission are enabled build a list
            if conf_file["ftp_ini"]["enabled"] == "y":
                ftp_file_list.append(out_filename)
        except NCOException as err:
            logger.error("Error executing ncks: %s", err, extra=metadata)
            sys.exit(1)

    # if enabled do upload
    if conf_file["ftp_ini"]["enabled"] == "y":
        logger.info("FTP Upload enabled")
        logger.debug("File to transmit: %s", ftp_file_list)
        logger.debug("Transmission parameter: %s", conf_file["ftp_ini"])
        ftp_transm_parameter = {
            'srv_address': conf_file["ftp_ini"]['server'],
            'ftp_usr': conf_file["ftp_ini"]['username'],
            'ftp_psw': conf_file["ftp_ini"]['password'],
            'ftp_path': conf_file["ftp_ini"]['remote_path']}
        if not utils_ftp.ftp_file_upload(ftp_transm_parameter, ftp_file_list):
            logger.error(
                "Something wrong with data transmission.",
                extra=metadata)
            exit(1)
    # Update metadata
    metadata["metadata"]["status"] = config["status"]["done"]
    logger.info("Run completed successfully", extra=metadata)


if __name__ == '__main__':
    main()
