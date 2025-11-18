from services.Evaluator import Evaluator

class ConfigDriver(Evaluator):
    def __init__(self, resource, client, resource_type):
        super().__init__()
        self.resource = resource
        self.client = client
        self.resource_type = resource_type
        self._resourceName = resource.get('name', 'ConfigService')
        self.init()

    def _checkConfigEnabled(self):
        if self.resource_type == 'service' and not self.resource:
            self.results['ConfigEnabled'] = [-1, 'Config not enabled']
        else:
            self.results['ConfigEnabled'] = [1, 'Config enabled']

    def _checkRecorderStatus(self):
        if self.resource_type == 'recorder':
            try:
                response = self.client.describe_configuration_recorder_status()
                statuses = response.get('ConfigurationRecordersStatus', [])
                recorder_status = next((s for s in statuses if s['name'] == self.resource['name']), None)
                
                if recorder_status and recorder_status.get('recording'):
                    self.results['RecorderStatus'] = [1, 'Recording active']
                else:
                    self.results['RecorderStatus'] = [-1, 'Recording inactive']
            except Exception:
                self.results['RecorderStatus'] = [-1, 'Unable to check status']

    def _checkDeliveryChannel(self):
        try:
            response = self.client.describe_delivery_channels()
            channels = response.get('DeliveryChannels', [])
            if channels:
                self.results['DeliveryChannel'] = [1, f'{len(channels)} delivery channels configured']
            else:
                self.results['DeliveryChannel'] = [-1, 'No delivery channels configured']
        except Exception:
            self.results['DeliveryChannel'] = [-1, 'Unable to check delivery channels']

    def _checkConfigRules(self):
        try:
            response = self.client.describe_config_rules()
            rules = response.get('ConfigRules', [])
            if len(rules) > 0:
                self.results['ConfigRules'] = [1, f'{len(rules)} config rules active']
            else:
                self.results['ConfigRules'] = [-1, 'No config rules configured']
        except Exception:
            self.results['ConfigRules'] = [-1, 'Unable to check config rules']

    def _checkComplianceStatus(self):
        try:
            response = self.client.get_compliance_summary_by_config_rule()
            summary = response.get('ComplianceSummary', {})
            non_compliant = summary.get('NonCompliantResourceCount', {}).get('CappedCount', 0)
            
            if non_compliant > 0:
                self.results['ComplianceStatus'] = [-1, f'{non_compliant} non-compliant resources']
            else:
                self.results['ComplianceStatus'] = [1, 'All resources compliant']
        except Exception:
            self.results['ComplianceStatus'] = [0, 'Unable to check compliance']