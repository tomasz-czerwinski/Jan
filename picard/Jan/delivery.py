#!/usr/bin/env python2.7

#INFO: Version 1.0.1

import os
import shutil
import logging

from protocol import svn_protocol, packet, http_protocol

#Logger Configuration
#logging.basicConfig(level=logging.INFO,
#                    filename='delivery.log', 
#                    filemode='w')

logger = logging.getLogger(__name__)


def deliver_factory(protocol, source=None, destination=None):
    """Objects factory."""
    logger.info("Delivery Factory: create delivery by protocol - {obj}, source - {source}, destination - {destination}".format(obj=protocol,source=source,destination=destination))

    if protocol == "files":
        return packet.packet(source, destination)
    elif protocol == "svn":
        return svn_protocol.protocol_svn(source, destination)
    elif protocol == "http":
        return http_protocol.protocol_http(source, destination)
    else: 
        logger.error("{p} is not supported!".format(p=str(protocol).upper()))
        raise Exception()


class delivery:

    def __init__(self, config, name):
        """Initialization delivery."""

        ### Delivery name
        self.delivery_name = name

        # Path to delivery workspace
        self.workspace = "/tmp/tmp_delivery_" + self.delivery_name

        # Configuration of delivery's packages
        # Configuration from we will download package and which protocol we will use
        if config.location:
            self.localization_from = "".join(config.location)
        if config.source_transport:
            self.protocol_from = "".join(config.source_transport)
        else:
            self.protocol_from = 'files'

        # Configuration of destination packages and protocol
        if config.destination:
            self.destination_of_packages = self.multideliveries("".join(config.destination))
        if config.destination_transport:
            self.protocol_to = self.multideliveries("".join(config.destination_transport))
        else:
            self.protocol_to = 'files'

        # Configuration of Packages 
        # Path to source data
        self.src_path = os.path.join(self.workspace, 'download_source')

        # List of temporary packages for delivering
        self.temporary_packages = []

        self.ignore = None

        self.rules = None

        #if config.from_place_rules is not None and config.to_place_rules is not None:
        #    self.rules = self.set_rules(config.from_place_rules, config.to_place_rules)

        # specific comment for delivery {name} please use to determinate product
        if config.special_word:
                self.special_word = "".join(config.special_word)
        else:
            self.special_word = ''

        if config.comment:
            self.comment = config.comment
        else:
            self.comment = None
        # Option will erase all files from destination packet and after that put only files from source
        self.force = None

        #logger.info("Create Delivery - NAME=\"{name}\", FROM=\"{fro}\", TO=\"{to}\"".format(name=self.delivery_name, fro=self.location_from, to=to) for to in self.destination_of_packages)

    def prepare_packages(self):
        """All actions which are necessary to prepare delivery."""

        logger.info("Prepare packages to delivery...")
        self.create_workspace()
        # Download source package
        self.download_source(self.protocol_from, self.localization_from, self.src_path)

        destination = zip(self.destination_of_packages, self.protocol_to)

        # Download target package
        for temp_dst, temp_protocol in destination:
            _temp_dst = temp_dst.split("/")[-1]
            temp_dst_path = os.path.join(self.workspace, _temp_dst)
            self.temporary_packages.append(self.download_package(temp_protocol, temp_dst_path, temp_dst))
        logger.info("Prepare package - Ok")
       
    def deliver_packages(self):
        logger.info("START Delivering packages...")
        for temp_dst in self.destination_of_packages:
            self.copy_package(temp_dst)
        for deliver in self.temporary_packages:
            if not self.comment:
                self.comment = "{} Delivery for {} ".format(self.special_word, self.delivery_name)
            deliver.deliver_package(self.comment)

        logger.info("Delivering packages - Ok!")

    def download_source(self, *args):
        self.download_package(*args)
 
    def download_package(self, protocol=None, source=None, destination=None):
        """Download or Copy packet for source packet ( http://, svn://, file:// etc.). """
        logger.info("Download_package... - protocol=\"{pro}\", from=\"{fro}\", to=\"{to}\"".format(pro=protocol, fro=source, to=destination))
        delivery = deliver_factory(protocol, source, destination)
        delivery.download_package()
        logger.info("OK")
        return delivery

    def copy_package(self, temp_dst):
        """ Copy source package to target package """
        temp_dst_path = os.path.join(self.workspace, temp_dst.split("/")[-1])
        _packet = packet.packet(self.src_path, temp_dst_path, self.ignore, self.rules)
        logger.info("Start copy source to temporary delivery directory ( \"{source}\" -> \"{temp_dst_path}\" )".format(source=self.src_path, temp_dst_path=temp_dst_path))
        _packet.copy()
        logger.info("Copy source to temporary delivery directory - OK!")

    def multideliveries(self, locations):
        locations = locations.split(',')
        return locations

    def create_workspace(self):
        """Method creates workspace for delivery."""
        logger.info("Create Workspace... - PATH=\"{workspace}\".".format(workspace=self.workspace))
        self.mkdir(self.workspace)
        logger.info("OK")

    def mkdir(self, path):
        try:
            os.mkdir(path)
        except OSError, what:
            logger.warning("\"{p}\" is not creating because {w}.".format(p=path, w=what))

    def set_rules(self, list_files_from, list_files_to):
        temp = {}

        for (k,v) in zip(list_files_from.split(','), list_files_to.split(',')):
            temp[k.strip()] = v.strip()
        return temp

    def clean(self):
        logger.info("CleanUp... - \"{p}\" ".format(p=self.workspace))
        shutil.rmtree(path=self.workspace, ignore_errors=True)
        logger.info("OK")


if __name__ == "__main__":
    import xml_config_parser
    import os
    path = os.path.join('configs', 'tup_unstable_flexi2-powerpc-e500-ose.xml')
    config = xml_config_parser.TagParser(path).parse()
    Delivery = delivery(config, 'test')
    Delivery.prepare_packages()
    Delivery.deliver_packages()


