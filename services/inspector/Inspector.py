import botocore
from utils.Config import Config
from services.Service import Service
from services.inspector.drivers.InspectorDriver import InspectorDriver
from utils.Tools import _pi

class Inspector(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        ssBoto = self.ssBoto
        self.inspectorClient = ssBoto.client('inspector2', config=self.bConfig)
    
    def getResources(self):
        try:
            response = self.inspectorClient.batch_get_account_status(accountIds=[])
            return [{'status': 'enabled'}]  # Simplified check
        except Exception as e:
            print(f"Inspector not available: {e}")
            return []
    
    def advise(self):
        objs = {}
        
        _pi('Inspector', 'Service')
        obj = InspectorDriver({}, self.inspectorClient)
        obj.run(self.__class__)
        objs["Service::Inspector"] = obj.getInfo()
        del obj
        
        return objs