import botocore
from utils.Config import Config
from services.Service import Service
from services.securityhub.drivers.SecurityHubDriver import SecurityHubDriver
from utils.Tools import _pi

class Securityhub(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        ssBoto = self.ssBoto
        self.securityHubClient = ssBoto.client('securityhub', config=self.bConfig)
    
    def getResources(self):
        try:
            response = self.securityHubClient.describe_hub()
            return [response]
        except Exception as e:
            print(f"Security Hub not enabled: {e}")
            return []
    
    def advise(self):
        objs = {}
        hubs = self.getResources()
        
        if hubs:
            for hub in hubs:
                _pi('SecurityHub', 'Hub')
                obj = SecurityHubDriver(hub, self.securityHubClient)
                obj.run(self.__class__)
                objs["Hub::SecurityHub"] = obj.getInfo()
                del obj
        else:
            _pi('SecurityHub', 'NotEnabled')
            obj = SecurityHubDriver({}, self.securityHubClient)
            obj.run(self.__class__)
            objs["Hub::NotEnabled"] = obj.getInfo()
            del obj
        
        return objs