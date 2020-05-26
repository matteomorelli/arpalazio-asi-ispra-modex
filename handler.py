# Copyright (c) 2020 ARPA Lazio <craria@arpalazio.it>
# SPDX-License-Identifier: EUPL-1.2

# Author: Matteo Morelli <matteo.morelli@gmail.com>

import logging
import logging.config
import traceback
import argparse
import configparser
import sys
from nco import Nco
from libs import utils_os
from libs import utils
from libs import utils_ftp

# Script version
VERSION = "0.0.1"

logging.config.fileConfig(
    'ini/logging.ini',
    disable_existing_loggers=False)
logger = logging.getLogger(__name__)


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
    args = parser.parse_args()

    args_value = {
        "ini_file": args.ini_file
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
    except:
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


def main():
    # Initialize value
    conf_file = None
    # Initialize argument parser
    parser = argparse.ArgumentParser()
    in_value = _define_check_args(parser)
    logger.debug("Passed arguments: %s", in_value)
    if utils_os.simple_file_read(in_value["ini_file"]):
        conf_file = _parse_configuration_value(in_value["ini_file"])
    if conf_file is None:
        logger.error("sys.exiting with error, check you logs")
        sys.exit(1)
    logger.debug("Configuration values: %s", conf_file)

    # Compose input filename based on model type and ini options
    # Simulating class output
    model_file = [
        "FARM_conc_g4_20200526+000-023.nc",
        "FARM_conc_g4_20200526+024-047.nc",
        "FARM_conc_g4_20200526+048-071.nc",
        "FARM_conc_g4_20200526+072-095.nc",
        "FARM_conc_g4_20200526+096-119.nc"]
    logger.info("Checking model data existence")
    if utils.is_empty(model_file):
        logger.error("Invalid filename list")
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
            logger.error("%s does not exist", in_filename)
            sys.exit(1)

        out_filename = conf_file["model_data"]["out_dir"] + \
            conf_file["model_data"]["out_prefix"] + \
            file_name
        # check output directory existence
        if not utils_os.is_valid_path(
                conf_file["model_data"]["out_dir"], "dir"):
            logger.error(
                "Directory %s does not exist",
                conf_file["model_data"]["out_dir"])
            sys.exit(1)
        try:
            logger.info("Parsing file: %s", in_filename)
            nco.ncks(input=in_filename, output=out_filename, options=ncks_opt)
            # if ftp transmission are enabled build a list
            if conf_file["ftp_ini"]["enabled"] == "y":
                ftp_file_list.append(out_filename)
        except:
            logger.error("uncaught exception: %s", traceback.format_exc())
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
            logger.error("Something wrong with data transmission.")
            exit(1)


if __name__ == '__main__':
    main()
