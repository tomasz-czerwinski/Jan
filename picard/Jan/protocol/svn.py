import pysvn
#TODO
# threaded version of getExternalsWithRevisions 
# feedback: mrB1ack (tomasz.czerwinski@nsn.com) 

#helper functions

def get_login(realm, username, may_save):

    """returned values:
        retcode - boolean, False if no username and password are available. 
		True if subversion is to use the username and password.
        username - string, the username to use
        password - string, the password to use
        save - boolean, return True if you want subversion to remember 
		the username and password in the configuration directory. 
		return False to prevent saving the username and password.
    """




#    print("[Info]\tAuthenticating with tupci"\
#    + " account name".format(name=pysvn.__name__) )

    #return True, 'tupci', '16b9e82b', False 
    return True, '*', '*', False 


def ssl_server_trust_prompt(trust_dict):

    """returned values
        retcode - boolean, False if no username and password are available.
		True if subversion is to use the username and password, but 
		I strongly suppose, there is a mistake in description. True 
		behavior is to acceppt certificate, false - to reject it.
        accepted_failures - int, the accepted failures allowed
        save - boolean, return True if you want subversion to remember 
		the certificate in the configuration directory. return 
		False to prevent saving the certificate.
    """
    
    printCertificate(trust_dict)
    return True, 1, False



def printCertificate(trustDict):
    print('Certificate info:')
    print("Hostname: {hostname}\n" \
	+ "Realm: {realm}\n" \
	+ "Fingerprint: {fingerprint}\n" \
	+ "Issuer name:{issuer_dname}\n" \
	+ "Valid from: {valid_from}\n" \
	+ "Valid until: {valid_until}".format(\
	hostname = trustDict['hostname'],\
	realm = trustDict['realm'],\
	fingerprint = trustDict['finger_print'],\
	issuer_dname = trustDict['issuer_dname'],\
	valid_from = trustDict['valid_from'],\
	valid_until = trustDict['valid_until'])\
	)

#main SVN class definition

class SVN:

    def __init__(self, repo, verbose=False):
        
        self.verbose = verbose

        #get URI
        self.repo = repo.rstrip('/')

        #initialize SVN client instance
        self.client = pysvn.Client()
        self.client.exception_style = 1

        #function bindings
        self.client.callback_get_login = get_login
        self.client.callback_ssl_server_trust_prompt = ssl_server_trust_prompt

    def info(self, path):
    #works with local repositories only
        
        if self.client:
            items = {} 
            
            entry = self.client.info( path ) 
            items['checksum'] = entry.checksum
            items['author'] = entry.commit_author
            items['revision'] = entry.commit_revision
            items['name'] = entry.name
            items['url'] = entry.url
            items['uuid'] = entry.uuid
            items['copy_from_revision'] = entry.copy_from_revision
            items['copy_from_url'] = entry.copy_from_url
            items['is_absent'] = entry.is_absent
            items['is_copied'] = entry.is_copied
            items['is_deleted'] = entry.is_deleted
            items['kind'] = entry.kind
            items['properties_time'] = entry.properties_time
            items['property_reject_file'] = entry.property_reject_file
            items['repos'] = entry.repos
            items['schedule'] = entry.schedule
            items['text_time'] = entry.text_time


            return items

        return None 


    def info2(self):
    #Universal

        if self.client:
            if self.verbose:
                print("[Info]\tFetching SVN info from: {repo}".format(repo=self.repo))


            items = {} 

            try:
                answer = self.client.info2( url_or_path = self.repo, recurse = False )
            except pysvn.ClientError, e:
                print("[Error]\tSVN client exception occured.")
                for message, code in e.args[1]:
                    print("\tCode: {c}\n\tDetails: {m}".format(c=code, m=message))
                return None	

            entry = answer[0][1]
            items['URL'] = entry.URL
            items['rev'] = entry.rev
            items['kind'] = entry.kind
            items['repos_root_URL'] = entry.repos_root_URL
            items['repos_UUID'] = entry.repos_UUID 
            items['last_changed_rev'] = entry.last_changed_rev 
            items['last_changed_date'] = entry.last_changed_date 
            items['last_changed_author'] = entry.last_changed_author 

            return items

        return None 


    def getExternals( self ):

        try:
            prop_dict = self.client.propget(\
					prop_name="svn:externals",\
					url_or_path=self.repo\
					)
            if len(prop_dict) > 0:
                return prop_dict[prop_dict.keys()[0]].splitlines()
              
        except:
            return None 



    def getProperty( self , prop ):

        try:
            prop_dict = self.client.propget(\
					prop_name="svn:{0}".format(prop),\
					url_or_path=self.repo\
					)
            if len(prop_dict) > 0:
                return prop_dict[prop_dict.keys()[0]]
              
        except:
            return None 


   
    def getExternalsWithRevisions ( self ):
    #may be time consuming

        extList = self.getExternals()

        if extList != None:
            for item in extList:
                if item.strip() and not item.startswith('#'):
                    print(self.repo + item.split()[0])




    def delExternals( self, repo ):
        
        try:
            self.client.propdel( prop_name="svn:externals", url_or_path=repo )
        except:
            return None 

        return 0

    
    def log( self, startRev = None, endRev = None ):

        if self.verbose:
            print("[Info]\tFetching SVN log from: {repo}".format(repo=self.repo))

        if startRev == None:
            start = pysvn.Revision( opt_revision_kind.head )
        else:
            start = pysvn.Revision( pysvn.opt_revision_kind.number, startRev )
 

        if endRev == None:
            end = pysvn.Revision( opt_revision_kind.number, 0 )
        else:
            end = pysvn.Revision( pysvn.opt_revision_kind.number, endRev )
        
        try:
            return  self.client.log( self.repo, start, end )
        
        except pysvn.ClientError, e:

            print("[Error]\tSVN client exception occured.")
            for message, code in e.args[1]:
                print("\tCode: {c}\n\tDetails: {m}".format(c=code, m=message))
		
            return None

    def checkout( self, path ):
        try:
            self.client.checkout( self.repo, path )

        except pysvn.ClientError, e:

            print("[Error]\tSVN client exception occured.")
            for message, code in e.args[1]:
                print("\tCode: {c}\n\tDetails: {m}".format(c=code, m=message))
            return None
        return 0

    def export( self, path ):
        try:
            self.client.export( self.repo, path )

        except pysvn.ClientError, e:

            print("[Error]\tSVN client exception occured.")
            for message, code in e.args[1]:
                print("\tCode: {c}\n\tDetails: {m}".format(c=code, m=message))
            return None
        return 0

    def remove( self, path ):
        try:
            self.client.remove( path )

        except pysvn.ClientError, e:

            print("[Error]\tSVN client exception occured.")
            for message, code in e.args[1]:
                print("\tCode: {c}\n\tDetails: {m}".format(c=code, m=message))


    def add( self, path ):
        try:
            self.client.add( path )

        except pysvn.ClientError, e:

            print("[Error]\tSVN client exception occured.")
            for message, code in e.args[1]:
                print("\tCode: {c}\n\tDetails: {m}".format(c=code, m=message))
            return None
        return 0

    def update( self, path ):
        try:
            self.client.update( path )

        except pysvn.ClientError, e:

            print("[Error]\tSVN client exception occured.")
            for message, code in e.args[1]:
                print("\tCode: {c}\n\tDetails: {m}".format(c=code, m=message))

    def checkin( self, path, comment=None ):
        try:
            self.client.checkin( path, comment )

        except pysvn.ClientError, e:

            print("[Error]\tSVN client exception occured.")
            for message, code in e.args[1]:
                print("\tCode: {c}\n\tDetails: {m}".format(c=code, m=message))
            return None
        return 0
