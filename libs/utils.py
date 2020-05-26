# Copyright (c) 2018 Matteo Morelli <matteo.morelli@gmail.com>
# SPDX-License-Identifier: EUPL-1.2

# Author: Matteo Morelli <matteo.morelli@gmail.com>

import logging
import datetime
from time import strptime
from libs import utils_os

# Libs version
VERSION = "1.0.3"

# Initialise logger
logger = logging.getLogger(__name__)


def validate_input_time(time_string, kind_of):
    # initialize local logger
    logger.debug("Time string: %s", time_string)
    allowed_kind = ["d", "h"]
    if kind_of in allowed_kind:
        logger.debug("Time kind passed validation")
        try:
            if kind_of == "d":
                logger.debug("Testing day unit")
                if time_string.count("/") == 2:
                    year, month, day = time_string.split("/")
                    datetime.datetime(int(year), int(month), int(day))
                    return True
            elif kind_of == "h":
                logger.debug("Testing hour unit")
                strptime(time_string, '%H:%M:%S')
                return True
        except ValueError:
            logger.error("Not a valid date or valid date format: %s",
                         time_string)
    return False


def is_empty(any_structure):
    logger.debug("Checking if empty data structure: %s", any_structure)
    if any_structure:
        # Structure is not empty
        return False
    else:
        # Structure is empty
        return True


def empty_value_in_dict(data):
    for key, value in data.items():
        logger.debug("Dict+value %s => %s", key, value)
        if isinstance(value, dict):
            # if value is a dict reiterate and check against itself
            if empty_value_in_dict(value):
                return True
        else:
            if not value:
                # Value is empty
                logger.debug("Dict empty value is %s => %s", key, value)
                return True
    return False


def validate_path(dict_path, kind_of):
    # Input:
    #   dict_path = an omogeneous dictionary of file path or dir path
    #   kind_of = which type to validate
    # Output:
    #   return false if even only a single path is not valid
    logger = logging.getLogger("__name__")
    allowed_kind = ["file", "dir"]
    control_list = []
    if isinstance(dict_path, dict) and kind_of in allowed_kind:
        for key, value in dict_path.items():
            logger.debug("Checking type %s on: %s", kind_of, value)
            if not utils_os.is_valid_path(value, kind_of):
                logger.error("Cannot access %s directory", key)
                control_list.append(value)
        logger.debug("Path control list: %s", control_list)
        if not control_list:
            return True
    return False


def validate_usr_input_polls(usr_list, valid_list):
    logger.debug("User list: %s", usr_list)
    logger.debug("Valid polls: %s", valid_list)
    if isinstance(usr_list, list) and isinstance(valid_list, list):
        # Clean from duplicate
        poll_list = list(set(usr_list))
        simple_poll_check = []
        for poll in poll_list:
            if poll not in valid_list:
                simple_poll_check.append(poll)
        if not simple_poll_check:
            return True
    logger.error(
        "Those pollutants are not allowed: %s",
        simple_poll_check
    )
    return False


def build_launch_parameter(conf_dict, procedure_name):
    logger.debug("Procedure: %s", procedure_name)
    logger.debug("Configuration dict: %s", conf_dict)
    allowed_procedure = ["post_gap", "post_surfpro", "post_chem"]
    if isinstance(conf_dict, dict) and procedure_name in allowed_procedure:
        logger.info("Building Launch config for: %s", procedure_name)
        if procedure_name is "post_gap":
            pass
