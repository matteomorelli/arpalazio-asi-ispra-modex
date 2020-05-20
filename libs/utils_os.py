# Copyright (c) 2018 Matteo Morelli <matteo.morelli@gmail.com>
# SPDX-License-Identifier: EUPL-1.2

# Author: Matteo Morelli <matteo.morelli@gmail.com>

import logging
import os
import json
import re

# Libs version
VERSION = "1.0.1"


def is_valid_path(path, kind):
    logger = logging.getLogger(__name__)
    valid_type = ["dir", "file"]
    logger.debug("Input parameter %s %s", path, kind)
    if kind in valid_type and isinstance(path, str):
        if kind == "dir":
            logger.debug("Checking if it's a directory")
            if os.path.isdir(path):
                return True
        if kind == "file":
            logger.debug("Checking if it's a file")
            if os.path.isfile(path):
                return True
    logger.debug("Path is not a valid %s", kind)
    return False


def simple_file_read(file_str):
    # initialize local logger
    logger = logging.getLogger(__name__)
    logger.debug("Testing file: %s", file_str)
    try:
        with open(file_str) as f:
            logger.debug("Reading file: %s", f)
            f.read()
            f.close()
    except IOError as err:
        # TODO: fail gracefuly and output with logger handler
        logger.warning("Error reading file %s: %s", file_str, err)
        return False
    return True


def read_local_json(input_file):
    logger = logging.getLogger(__name__)
    logger.info("Opening file: %s", input_file)
    try:
        # open file in read mode
        with open(input_file, 'r') as f:
            content = json.load(f)
        f.close()
        return content
    except Exception as e:
        logger.error("Unable to open file %s: %s", input_file, e)
        raise Exception(e)


def find_files_with_prefix(prefix, path):
    logger = logging.getLogger(__name__)
    # Code from https://dzone.com/articles/listing-a-directory-with-python
    pattern = "^" + prefix
    logger.debug("Looking for pattern: %s", pattern)
    rx = re.compile(pattern)
    file_list = []
    for path, dnames, fnames in os.walk(path):
        file_list.extend(
            [os.path.join(path, x) for x in fnames if rx.search(x)]
        )
    logger.debug("File list: %s", file_list)
    if file_list:
        return file_list
    return False


def find_files_containing(string, path, file_ext=None):
    logger = logging.getLogger(__name__)
    if isinstance(path, str) and os.path.isdir(path):
        pattern = string
        if file_ext is not None:
            pattern = string + "\\S+\\" + file_ext + "$"
        logger.debug("Looking for pattern: %s", pattern)
        # Code from https://dzone.com/articles/listing-a-directory-with-python
        rx = re.compile(pattern)
        file_list = []
        for path, dnames, fnames in os.walk(path):
            file_list.extend(
                [os.path.join(path, x) for x in fnames if rx.search(x)]
            )
        logger.debug("File list: %s", file_list)
        if file_list:
            return file_list
    return False


def empty_dir_from_files(path):
    logger = logging.getLogger(__name__)
    if isinstance(path, str) and os.path.isdir(path):
        logger.debug("Empting folder: %s", path)
        for path, dnames, fnames in os.walk(path):
            for file in fnames:
                to_be_removed = os.path.join(path, file)
                logger.debug("Removing file: %s", to_be_removed)
                try:
                    os.remove(to_be_removed)
                except OSError as err:
                    logger.error(
                        "Error removing file, error: %s",
                        err,
                        exc_info=True
                    )
        return True
    return False


def simple_remove_dir(path):
    logger = logging.getLogger(__name__)
    if isinstance(path, str) and os.path.isdir(path):
        logger.debug("Removing folder: %s", path)
        try:
            os.removedirs(path)
        except OSError as err:
            logger.error(
                "Error removing folder, error: %s",
                err,
                exc_info=True
            )
        return True
    return False
