# Copyright (c) 2020 Matteo Morelli <matteo.morelli@gmail.com>
# SPDX-License-Identifier: EUPL-1.2

# Author: Matteo Morelli <matteo.morelli@gmail.com>

import logging
import ftplib

# Libs version
VERSION = "2.0.0"


def ftp_file_upload(connection_parameter, file_list):
    ##############################################
    # Function to chek valid input format
    # Arguments:
    #   a dictionary with all the connection parameters
    #   a list containing a list() of file path to upload
    #
    #   connection_parameter = {'srv_address': 'xxx.xxx.xxx.xxx',
    #                           'ftp_usr': 'username',
    #                           'ftp_psw': 'password',
    #                           'ftp_path': '/path/to/upload/'}
    # Returns:
    #   true if all files were uploaded
    #   false if something goes wrong
    ##############################################
    # TODO: Handle upload of different file type based on extension.
    logger = logging.getLogger(__name__)
    # Server address is a requirement.
    if not connection_parameter['srv_address']:
        logger.error("No FTP server address")
        return False
    if not file_list:
        logger.error("No data to transmit")
        return False
    remote = ftplib.FTP()
    try:
        logger.info("Connecting to %s", connection_parameter['srv_address'])
        remote.connect(connection_parameter['srv_address'], 21, 60)
        remote.login(connection_parameter['ftp_usr'],
                     connection_parameter['ftp_psw'])
        # Forcing passive mode
        remote.set_pasv(True)
        logger.info(
            "Moving into remote dir: %s",
            connection_parameter['ftp_path']
        )
        remote.cwd(connection_parameter['ftp_path'])
    except ftplib.all_errors as ftperr:
        logger.error(
            "Error during FTP transmission: %s",
            ftperr,
            exc_info=True
        )
        return False

    if not file_list:
        logger.warning("No file passed for upload")
        remote.close()
        return False

    # List for upload status
    upload_status = list()
    for upload in file_list:
        if upload == '':
            logger.error("Cowardly refusing to transmit an empty string...")
            upload_status.append(False)
            continue
        logger.info("Uploading file: %s", upload)
        try:
            with open(upload, 'rb') as fp:
                # Getting only the filename for
                # ftp server compatibility (filezilla)
                filename = upload.split("/")[-1]
                # remote.storlines('STOR ' + filename, fp)
                remote.storbinary('STOR ' + filename, fp)
                upload_status.append(True)
        except IOError as file_err:
            logger.error("Error transferring file %s", upload)
            logger.error(
                "Error during FILE operation: %s",
                file_err,
                exc_info=True
            )
            upload_status.append(False)
        except ftplib.all_errors as ftp_err:
            logger.error("Error transferring file %s", upload)
            logger.error(
                "Error during FILE operation: %s",
                ftp_err,
                exc_info=True
            )
            upload_status.append(False)

    logger.info(
        "Closing connection to %s",
        connection_parameter['srv_address']
    )
    remote.close()
    if False in upload_status:
        return False
    # If everything is fine exit with true!
    return True
