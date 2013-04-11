import svn
import os
import packet
import logging


#Logger Configuration
#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

#TODO:
# Exception's Class...

class protocol_svn:
    def __init__(self, path, location):
        self.location = location
        self.path = path
        if self.location.split("/")[-1] == 'download_source':
            self.path, self.location = self.location, self.path
        self.repo = svn.SVN(self.location)
        self.repo_structure = packet.packet(self.path, self.path, ignore=[".svn"])
        logger.info("path - {p}, location - {l}".format(p=self.path,l=self.location))

    def download_package(self):
        if self.path.split("/")[-1] == 'download_source':
            if self.repo.export(self.path) is None:
                logger.error("Sesion will be terminated. Couldn't export repository...")
                exit()
        else:
            if self.repo.checkout(self.path) is None:
                logger.error("Sesion will be terminated. Couldn't checkout repository...")
                exit()
            self.remove_files()

    def deliver_package(self, comment):
        self.repo_structure.create_packet_structure()
        self.add_file()
        logger.info("Commiting files to {p} with commit - \"{commit}\"".format(p=self.path, commit=comment))
        if self.repo.checkin(self.path, comment) is None:
            logger.error("Sesion will be terminated. Couldn't checkin to repository...")
            exit()
        
    def add_file(self):
        for afile in self.repo_structure.files.keys():
            logger.info("Adding \"{f}\"".format(f=os.path.join(self.path, afile)))
            if self.repo.add(os.path.join(self.path, afile)) is None:
                self.repo.add(os.path.join(self.path, afile.split("/")[0]))

    def remove_files(self):
        self.repo_structure.create_packet_structure()
        for afile in self.repo_structure.files.keys():
            logger.info("Remove from repository \"{f}\"".format(f=os.path.join(self.path, afile)))
            self.repo.remove(os.path.join(self.path, afile))

