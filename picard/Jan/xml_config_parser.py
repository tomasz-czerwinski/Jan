from xml.etree.ElementTree import XMLParser
import sys

class GetXmlAttrs:

    def __init__(self):
        
        self.depth = 0
        self.maxDepth = 0

        self.attrs = {}
        self.current_tag = ''
        self.enter_data_tag = ''

        self.tag_source = ''
        self.tag_destination = ''

    def __getattr__(self, key):
        if key not in self.attrs.keys():
            return None
        else:
            return self.attrs.get(key, None)

    def start(self, tag, attrib):
        self.depth += 1

        if self.depth > self.maxDepth:
            self.maxDepth = self.depth
        
        if self.depth == 2:
            self.attrs[tag] = []
            self.current_tag = tag

        if self.depth == 4:
            self.enter_data_tag = tag

    def end(self, tag):
        self.depth -= 1

    def data(self, data):
        data = data.strip()

        if self.depth == 2:
            if data != '':
                self.attrs[self.current_tag].append((data))

        if self.depth == 4:
            if self.enter_data_tag == 'source':
                self.tag_source = data

            if self.enter_data_tag == 'destination':
                self.tag_destination = data
        
            if  self.tag_source != '' and self.tag_destination != '':
                self.attrs[self.current_tag].append((self.tag_source, self.tag_destination))

    def close(self):
        return self.attrs

class TagParser:
    """
    Usage as module:

    from xml_config_parser import TagParser
    handler = TagParser('example_file.xml').parse()
    handler.<tag> <-- Return content from tag 
    ------------------------------------------------

    Example:

    >>> from xml_config_parser import TagParser
    >>> handler = TagParser('config_example.xml').parse()
    >>> handler.source_transport
    ['http']
    >>> handler.destination_transport
    ['svn']
    
    ------------------------------------------------
    """
    def __init__(self, config=None):
            self.config = config

    def parse(self):
        target = GetXmlAttrs()
        parser = XMLParser(target=target)
        if self.config:
            parser.feed(self.config)

        return target

if __name__ == '__main__':

    import doctest

    if len(sys.argv) < 2:
        print "Usage: python %s <file>" % (sys.argv[0])

    else:
        status = doctest.testmod()
        sys.exit(status)


