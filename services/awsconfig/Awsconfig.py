import botocore
from utils.Config import Config as UtilConfig
from services.Service import Service
from services.awsconfig.drivers.ConfigDriver import ConfigDriver
from utils.Tools import _pi

class Awsconfig(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        ssBoto = self.ssBoto
        self.configClient = ssBoto.client('config', config=self.bConfig)
    
    def getResources(self):
        try:
            response = self.configClient.describe_configuration_recorders()
            recorders = response.get('ConfigurationRecorders', [])
            return recorders
        except Exception as e:
            print(f"Error getting config recorders: {e}")
            return []
    
    def advise(self):
        objs = {}
        
        # Check configuration recorders
        recorders = self.getResources()
        if recorders:
            for recorder in recorders:
                _pi('ConfigRecorder', recorder['name'])
                obj = ConfigDriver(recorder, self.configClient, 'recorder')
                obj.run(self.__class__)
                objs["Recorder::" + recorder['name']] = obj.getInfo()
                del obj
        else:
            # No recorders found - create a placeholder check
            _pi('ConfigService', 'NotConfigured')
            obj = ConfigDriver({}, self.configClient, 'service')
            obj.run(self.__class__)
            objs["Service::NotConfigured"] = obj.getInfo()
            del obj
        
        return objs