import os
import shutil
import fnmatch
import logging

#Logger Configuration
#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class packet:
    """Packet is representation of files structure:

    SetUp()

        >>> test_source = "test_source"
        >>> test_package = "test"
        >>> excluded_package = "excluded_file"
        >>> os.mkdir(test_source)

        >>> Test = packet(test_source)
        >>> Test.target = test_source

        >>> path = os.path.join(test_source, test_package)
        >>> path2 = os.path.join(test_source, excluded_package)
        >>> f = open(path, "w")
        >>> f.write('This is a test file')
        >>> f.close()
        >>> f = open(path2, "w")
        >>> f.write("This file will be excluded.")
        >>> f.close()

    Packet can be initialized by path. You can provide new object by real or abs path. If you don't provide a parameter with absolutized version of the pathname. Created object will start from current directory.
    
        >>> T = packet()
        >>> T = packet("test")
        >>> T = packet(target="target")
        >>> T = packet(test_source, "target")
        
    Copy method can be run without parameters. It will use dictionary self.files to figure on where have to been copy files. E.g. self.files contain 'a':'a' what mean that file 'a' is going to self.path + 'a' in target packet.

        >>> T.rules = {test_package: test_package}

                          source --> target
        >>> T.copy()
        >>> os.path.exists(os.path.abspath(os.path.join(T.target, test_package)))
        True

        >>> T.remove_files()

    Copy method is excluding files/dirs which name is starting with e* e.g eeee, elf 

        >>> T.rules = None
        >>> T.ignore = ["e*"]
        >>> T.copy()
        >>> os.path.exists(os.path.abspath(os.path.join(T.target, excluded_package)))
        False

        >>> T.remove_files()

    CleanUp !

        >>> Test.remove_files()

    """

    def __init__(self, path=None, target=None, ignore=None, rules=None):
        #path in folder structure : target path in structure
        self.files = {}
        self.path = path
        self.target = target
        self.ignore = ignore
        self.rules = rules
        logger.info("Initialized Object - PATH=\"{path}\" TARGET=\"{target}\"".format(path=self.path, target=self.target))

    def deliver_package(self):
        logger.info("Delivering from \"{path}\" to \"{target}\"".format(path=self.path,target=self.target))
        self.copy()
    
    def download_package(self):
        if not os.path.exists(self.path):
            logger.info("Create DIR=\"{d}\"".format(d=self.path))
            os.mkdir(self.path)
        self.copy()

    def copy(self):
        """Copy files between source and destination packets."""
        source = os.path.abspath(self.path)
        destination = os.path.abspath(self.target)

        logger.info("Running Copy Method - SOURCE=\"{src}\" DESTINATION=\"{dst}\" IGNORE=\"{ignore}\"".format(src=source, dst=destination, ignore=self.ignore))

        if not os.path.exists(source):
            logger.error("\"{source}\" PATH DOESN'T EXIST. PROGRAM TERMINATED. Please check log file.".format(source=source))

        if self.rules is not None:
            files = self.rules
        else:
            self.create_packet_structure(source)
            files = self.files

        for (k,v) in files.items():
            src = os.path.join(source,k)
            dst = os.path.join(destination,v)
            dirpath = os.path.dirname(dst)
            if not os.path.isdir(dirpath):
                logger.info("Create directory - \"{dst}\"".format(dst=dirpath))
                os.makedirs(dirpath)
            logger.info("copy from \"{f}\" to \"{t}\"".format(f=src,t=dst))
            shutil.copyfile(src,dst)
        logger.info("OK")

    def ignore_patterns(self, relpath):
        """It's using easy patterns to exclude files/dirs from package.
        
        options:

            * - matches everything
            ? - matches any single character

        """
        names = relpath.split('/')
        for name in names:
            for pattern in self.ignore:
                if fnmatch.fnmatch(name, pattern):
                    return True
        return False

    def create_packet_structure(self, path=None):
        tmp_files = {}
        if path is None:
            path = self.target
        logger.info("Create packet structure - PATH=\"{path}\"".format(path=path))
        for root,dirs,files in os.walk(path):
            for afile in files:
                tmp = os.path.relpath((os.path.join(root,afile)),path)
                if self.ignore is not None and self.ignore_patterns(tmp):
                    logger.info("Omit file \"{f}\"".format(f=tmp))
                    continue
                tmp_files[tmp] = tmp
        self.files = tmp_files
        logger.info("OK")

    def remove_files(self, path=None):
        if path is None:
            path = self.target
        logger.info("Removing files - PATH=\"{p}\"".format(p=path))
        for afile, path_to_afile in self.files.items():
            tmp = os.path.join(path, path_to_afile)
            try:
                logger.info("Delete \"{name}\" from packet structure".format(name=tmp))
                os.remove(tmp)
            except os.error, err:
                onerror(os.remove, fullname, sys.exc_info())

        logger.info("OK")

    def info(self):
        """Print configuration of packet."""
        print "root path = {path}".format(path=self.path)
        print "target path = {target}".format(target=self.target)
        print "files = {dic}".format(dic=self.files)

    def packet_info(self):
        if self.files:
            for (k,v) in self.files.items():
                print self.path + '/' + k,self.path + '/' + v
        else:
            logger.info("Packet's structure isn't creating.")

if __name__ == "__main__":
    import doctest
    status = doctest.testmod()[0]
    exit(status)
    

