# Copyright (c) 2020 ARPA Lazio <craria@arpalazio.it>
# SPDX-License-Identifier: EUPL-1.2

# Author: Matteo Morelli <matteo.morelli@gmail.com>

import logging
import logging.config
import traceback
import argparse
import configparser
import sys
from libs import utils_os
from libs import utils

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
            'out_dir': cfg.get("model_data", "out_dir").strip("\"")
        }
        ftp_ini = {
            'user': cfg.get("ftp", "user").strip("\""),
            'password': cfg.get("ftp", "password").strip("\"")
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


if __name__ == '__main__':
    main()
