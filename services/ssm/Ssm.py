import botocore
from utils.Config import Config
from services.Service import Service
from services.ssm.drivers.SSMDriver import SSMDriver
from utils.Tools import _pi

class Ssm(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        ssBoto = self.ssBoto
        self.ssmClient = ssBoto.client('ssm', config=self.bConfig)
    
    def getResources(self):
        try:
            response = self.ssmClient.describe_instance_information()
            instances = response.get('InstanceInformationList', [])
            return instances
        except Exception as e:
            print(f"Error getting SSM instances: {e}")
            return []
    
    def advise(self):
        objs = {}
        
        _pi('SystemsManager', 'Service')
        obj = SSMDriver({}, self.ssmClient)
        obj.run(self.__class__)
        objs["Service::SSM"] = obj.getInfo()
        del obj
        
        return objs