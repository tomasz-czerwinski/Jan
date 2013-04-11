import urllib
import os
import logging
import tarfile
import zipfile
import shutil

#Logger Configuration
#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class protocol_http:
    """Download package or packages from specific urls. It handle compressed packages.

    Object SetUp, takes in parameter more than one url.
        #>>> url = "http://jenkins.emea.nsn-net.net/job/TUP_WN7.0_unstable/lastSuccessfulBuild/artifact/C_Application/*zip*/C_Application.zip, http://jenkins.emea.nsn-net.net/job/TUP_WN7.0_unstable/lastSuccessfulBuild/artifact/C_Application/SC_TUP/Target/ReleaseNote.xml"
        
        >>> url = "http://127.0.0.1:8080/view/Modules%20DocTests/job/promotionXmlConfig/ws/protocol/*zip*/protocol.zip, http://127.0.0.1:8080/view/Modules%20DocTests/job/promotionXmlConfig/ws/delivery.py"
        >>> T = protocol_http(url, 'a')
        
    It will start download packages. To specific path or to current working directory.
        >>> T.download_package()

        >>> os.path.exists(T.path)
        True
    
    """
    def __init__ (self, location, path='.'):
        self.location = location.split(',')
        self.path = path
        self.extention = ['tgz','zip']

    def download_package(self):
        if not os.path.exists(self.path): 
            os.mkdir(self.path)
        for location in self.location:
            name = location.split('/')[-1]
            path = os.path.join(self.path, name)
            self.retrieve(location, path)
            extention = name.split('.')[-1]
            if extention in self.extention:
                getattr(self, "uncompress_" + str(extention))(path)
                os.remove(path)

    def retrieve(self, url, path):
        urllib.urlretrieve(url, path)

    def uncompress_zip(self, path):
        zipf = zipfile.ZipFile(path)
        zipf.extractall(self.path)

    def uncompress_tgz(self, path):
        tarfile = tarfiles.open(path)
        tarfile.extractall(self.path)
        tarfile.close()


if __name__ == "__main__":
    import doctest
    status = doctest.testmod()[0]
    exit(status)
    
    
