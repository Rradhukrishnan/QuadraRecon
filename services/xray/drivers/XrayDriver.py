from services.Evaluator import Evaluator
from botocore.exceptions import ClientError

class XrayDriver(Evaluator):
    def __init__(self, resource, client):
        super().__init__()
        self.resource = resource
        self.client = client
        self._resourceName = resource.get('Name', 'XRayService')
        self.init()

    def _checkTracingEnabled(self):
        try:
            response = self.client.get_tracing_config()
            tracing_config = response.get('TracingConfig', {})
            
            if tracing_config.get('Mode') == 'Active':
                self.results['TracingEnabled'] = [1, 'X-Ray tracing is active']
            else:
                self.results['TracingEnabled'] = [-1, 'X-Ray tracing not active']
        except ClientError:
            self.results['TracingEnabled'] = [-1, 'Unable to check tracing status']

    def _checkServiceMap(self):
        if self.resource:
            edges = self.resource.get('Edges', [])
            if len(edges) > 0:
                self.results['ServiceMap'] = [1, f'Service has {len(edges)} connections']
            else:
                self.results['ServiceMap'] = [-1, 'Service has no connections in service map']
        else:
            self.results['ServiceMap'] = [-1, 'No service map data available']

    def _checkEncryption(self):
        try:
            response = self.client.get_encryption_config()
            encryption_config = response.get('EncryptionConfig', {})
            
            if encryption_config.get('Type') == 'KMS':
                self.results['EncryptionEnabled'] = [1, 'X-Ray encryption enabled with KMS']
            else:
                self.results['EncryptionEnabled'] = [-1, 'X-Ray encryption not configured']
        except ClientError:
            self.results['EncryptionEnabled'] = [0, 'Unable to check encryption status']

    def _checkSamplingRules(self):
        try:
            response = self.client.get_sampling_rules()
            rules = response.get('SamplingRuleRecords', [])
            
            if len(rules) > 0:
                self.results['SamplingRules'] = [1, f'{len(rules)} sampling rules configured']
            else:
                self.results['SamplingRules'] = [-1, 'No custom sampling rules configured']
        except ClientError:
            self.results['SamplingRules'] = [0, 'Unable to check sampling rules']