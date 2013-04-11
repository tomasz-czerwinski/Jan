class Api:

    def __init__(self, request):
        self.parsed = False
        self.request = request
        self.data = {}
        self.error = ""

    def parse(self, info):
        
        if self.request.method == 'GET':
            for i in info:
                item = self.request.GET.get(i)
                if item:
                    self.data[i] = item  
                else:
                    self.error = "Data request from query failed. Requested item has not been found: '{item}'".format(item=i)
                    self.parsed = False
                    return 

        self.parsed = True    
    
    def get(self,info):
        if not self.parsed:
            self.parse(info)
        if self.parsed:
            return self.data
        else:
            return None


    def exception(self):
        return self.error


    def sanitize(self):
        pass
        #date=datetime.datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S")


