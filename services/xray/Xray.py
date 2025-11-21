import botocore
from utils.Config import Config
from services.Service import Service
from services.xray.drivers.XrayDriver import XrayDriver
from utils.Tools import _pi, _warn
from botocore.exceptions import ClientError

class Xray(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        ssBoto = self.ssBoto
        self.xrayClient = ssBoto.client('xray', config=self.bConfig)
    
    def get_resources(self):
        try:
            response = self.xrayClient.get_service_graph()
            services = response.get('Services', [])
            return services
        except ClientError as e:
            _warn(f"X-Ray service not available: {e}")
            return []
    
    def advise(self):
        objs = {}
        services = self.get_resources()
        
        if services:
            for service in services:
                service_name = service.get('Name', 'UnknownService')
                _pi('XRay', service_name)
                obj = XrayDriver(service, self.xrayClient)
                obj.run(self.__class__)
                objs[f"Service::{service_name}"] = obj.getInfo()
        else:
            _pi('XRay', 'Service')
            obj = XrayDriver({}, self.xrayClient)
            obj.run(self.__class__)
            objs["Service::XRay"] = obj.getInfo()
        
        return objs