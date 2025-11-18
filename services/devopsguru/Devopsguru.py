import botocore
from utils.Config import Config
from services.Service import Service
from services.devopsguru.drivers.DevOpsGuruDriver import DevOpsGuruDriver
from utils.Tools import _pi

class Devopsguru(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        ssBoto = self.ssBoto
        self.devopsGuruClient = ssBoto.client('devops-guru', config=self.bConfig)
    
    def getResources(self):
        try:
            response = self.devopsGuruClient.describe_service_integration()
            return [response]
        except Exception as e:
            print(f"DevOps Guru not available: {e}")
            return []
    
    def advise(self):
        objs = {}
        
        _pi('DevOpsGuru', 'Service')
        obj = DevOpsGuruDriver({}, self.devopsGuruClient)
        obj.run(self.__class__)
        objs["Service::DevOpsGuru"] = obj.getInfo()
        del obj
        
        return objs