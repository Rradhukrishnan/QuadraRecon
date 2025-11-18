import botocore
from utils.Config import Config as UtilConfig
from services.Service import Service
from services.awsconfig.drivers.ConfigDriver import ConfigDriver
from utils.Tools import _pi, _warn
from botocore.exceptions import ClientError

class Config(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        ssBoto = self.ssBoto
        self.configClient = ssBoto.client('config', config=self.bConfig)
    
    def get_resources(self):
        try:
            response = self.configClient.describe_configuration_recorders()
            recorders = response.get('ConfigurationRecorders', [])
            return recorders
        except ClientError as e:
            _warn(f"Config service not available: {e}")
            return []
    
    def advise(self):
        objs = {}
        recorders = self.get_resources()
        
        if recorders:
            for recorder in recorders:
                _pi('Config', recorder['name'])
                obj = ConfigDriver(recorder, self.configClient)
                obj.run(self.__class__)
                objs[f"Recorder::{recorder['name']}"] = obj.getInfo()
        else:
            _pi('Config', 'Service')
            obj = ConfigDriver({}, self.configClient)
            obj.run(self.__class__)
            objs["Service::Config"] = obj.getInfo()
        
        return objs