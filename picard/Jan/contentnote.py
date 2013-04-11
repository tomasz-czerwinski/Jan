import xml.dom.minidom
import urllib2
import datetime
import lexer


class ContentNote:
    def __init__(self, link):
        self.link = link
        self.options = {}
        self.parsed = False
        self.rawxml = None
        self.error = ""

    def parse(self):

        tmp_dict = dict()
        tmp_list = []

        if not self.rawxml:
            self.raw()

        if self.rawxml:
            note = xml.dom.minidom.parseString(self.rawxml)

            origin = note.getElementsByTagName("origin")[0]
            self.options['location'] = origin.getAttribute('location')
            self.options['revision'] = origin.getAttribute('revision')

            name = note.getElementsByTagName("name")[0]
            self.options['name'] = name.firstChild.data.strip()

            system = note.getElementsByTagName("system")[0]
            self.options['system'] = system.firstChild.data.strip()

            compilation_date = note.getElementsByTagName("releaseTime")[0]
            self.options['compilation_date'] = datetime.datetime.strptime(compilation_date.firstChild.data.strip(),
                                                                          "%Y-%m-%dT%H:%M:%S.%f")

            if note.getElementsByTagName("module"):
                module = note.getElementsByTagName("module")[0]
                self.options['module'] = module.getAttribute('name')

            faultLogInfo = note.getElementsByTagName("faultLogInfo")[0]
            self.options['fault_log_location'] = faultLogInfo.getAttribute('faultLogLocation')
            self.options['fault_log_start'] = faultLogInfo.getAttribute('faultLogStart')
            self.options['fault_log_end'] = faultLogInfo.getAttribute('faultLogEnd')

            faults = note.getElementsByTagName("fault")
            for fault in faults:
                tmp_dict = {}
                tmp_dict['revision'] = fault.getAttribute('baseline')
                tmp_dict['pronto'] = fault.getAttribute('id')
                tmp_dict['info'] = fault.getAttribute('info')
                tmp_dict['partial'] = fault.getAttribute('partial_fix')
                if tmp_dict['partial'] == 'false':
                    tmp_dict['partial'] == False
                else:
                    tmp_dict['partial'] == True
                tmp_dict['description'] = fault.firstChild.data.strip()
                tmp_list.append(tmp_dict)

            self.options['faults'] = tmp_list

            tmp_list = []
            baselines = note.getElementsByTagName("baseline")
            for baseline in baselines:
                tmp_dict = {}
                tmp_dict['name'] = baseline.getAttribute('name')
                tmp_dict['description'] = baseline.firstChild.data.strip()
                tmp_list.append(tmp_dict)

            self.options['baselines'] = tmp_list

            tmp_list = []
            externals = note.getElementsByTagName("external")
            for external in externals:
                tmp_dict = {}
                tmp_dict['description'] = external.firstChild.data.strip()
                tmp_list.append(tmp_dict)

            self.options['externals'] = tmp_list

            self.parsed = True

        else:
            return None

    def isParsed(self):
        return self.parsed

    def show(self):
        print self.options

    def get(self):

        if not self.parsed:
            self.parse()

        if self.parsed:
            return self.options
        else:
            return None

    def raw(self):

        if not self.rawxml:
            try:
                self.rawxml = urllib2.urlopen(self.link).read()

            except urllib2.HTTPError, e:
                self.error = "Error while fetching {link}:\n{description}".format(link=self.link, description=e)
                return None

        return self.rawxml

    def exception(self):
        return self.error

    def faultLogAsDomObject(self, log, patterns, relaxField):

        buf = []
        xmlFactory = xml.dom.minidom.Document()
        svnFaults = xmlFactory.createElement("correctedFaults")

        #if there's not log return empty object
        if not log:
            return svnFaults

        svnModule = xmlFactory.createElement("module")
        svnModule.setAttribute("name", "CPLANE TUP")

        for svnLog in log:
            lex = lexer.Lexer(
                unicode(svnLog.message, 'utf-8', 'strict').encode('ascii', 'ignore'),
                patterns,
                False
            )
            parsedLog = lex.parse()

            if not set(patterns.keys()).intersection(set(parsedLog.keys())):
                print("[Critical]\tAlien SVN log message has been found.\n"
                      + "\tConfig patterns doesn't fit to svn log message\n"
                      + "\tMost probably you are trying to generate release note on a different location\n"
                      + "\tthan config is binded to. You may use --raw option to enforce generation")
                exit(-1)

            if relaxField in parsedLog.keys():
                continue

            comment = " ".join(parsedLog['pronto'][1:])
            if "COMPLETED" == " ".join(parsedLog['readiness'][1:]).upper():
                readiness = "false"
            else:
                readiness = "true"
            inspector = " ".join(parsedLog['inspector'][1:])

            svnFault = xmlFactory.createElement("fault")
            svnFault.setAttribute("info", inspector)
            svnFault.setAttribute("id", parsedLog['pronto'][0].strip(':'))
            svnFault.setAttribute("partial_fix", str(readiness))
            svnFault.setAttribute("baseline", str(svnLog.revision.number))
            svnFaultContent = xmlFactory.createTextNode(
                unicode(comment, 'utf-8', 'strict').encode('ascii', 'xmlcharrefreplace'))
            svnFault.appendChild(svnFaultContent)
            svnModule.appendChild(svnFault)

        svnFaults.appendChild(svnModule)

        return svnFaults

    def faultLogAsListOfDictionaries(self, log, patterns, relaxField):

        faultLog = []
        faultDictionary = {}

        #if there's not log return None
        if not log:
            return None

        for svnLog in log:
            lex = lexer.Lexer(
                unicode(svnLog.message, 'utf-8', 'strict').encode('ascii', 'ignore'),
                patterns,
                False
            )
            parsedLog = lex.parse()

            if not set(patterns.keys()).intersection(set(parsedLog.keys())):
                print("[Critical]\tAlien SVN log message has been found.\n"
                      + "\tConfig patterns doesn't fit to svn log message\n"
                      + "\tMost probably you are trying to generate release note on a different location\n"
                      + "\tthan config is binded to. You may use --raw option to enforce generation")
                exit(-1)

            if relaxField in parsedLog.keys():
                continue

            comment = " ".join(parsedLog['pronto'][1:])
            if "COMPLETED" == " ".join(parsedLog['readiness'][1:]).upper():
                readiness = "false"
            else:
                readiness = "true"
            inspector = " ".join(parsedLog['inspector'][1:])

            faultDictionary["info"] = inspector
            faultDictionary["pronto"] = parsedLog['pronto'][0].strip(':')
            faultDictionary["partial"] = str(readiness)
            faultDictionary["revision"] = str(svnLog.revision.number)
            faultDictionary["description"] = unicode(comment, 'utf-8', 'strict').encode('ascii', 'xmlcharrefreplace')

            faultLog.append(faultDictionary)
            faultDictionary = {}

        return faultLog 
    

