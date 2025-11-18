import botocore
from utils.Config import Config
from services.Service import Service
from services.accessanalyzer.drivers.AccessAnalyzerDriver import AccessAnalyzerDriver
from utils.Tools import _pi

class Accessanalyzer(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        ssBoto = self.ssBoto
        self.accessAnalyzerClient = ssBoto.client('accessanalyzer', config=self.bConfig)
    
    def getResources(self):
        analyzers = []
        try:
            response = self.accessAnalyzerClient.list_analyzers()
            analyzers = response.get('analyzers', [])
        except Exception as e:
            print(f"Error listing analyzers: {e}")
        return analyzers
    
    def advise(self):
        objs = {}
        analyzers = self.getResources()
        
        for analyzer in analyzers:
            _pi('AccessAnalyzer', analyzer['name'])
            obj = AccessAnalyzerDriver(analyzer, self.accessAnalyzerClient)
            obj.run(self.__class__)
            objs["Analyzer::" + analyzer['name']] = obj.getInfo()
            del obj
        
        return objs