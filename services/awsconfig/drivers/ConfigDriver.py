from services.Evaluator import Evaluator
from botocore.exceptions import ClientError

class ConfigDriver(Evaluator):
    def __init__(self, resource, client):
        super().__init__()
        self.resource = resource
        self.client = client
        self._resourceName = resource.get('name', 'ConfigService')
        self.init()

    def _checkConfigEnabled(self):
        if not self.resource:
            self.results['ConfigEnabled'] = [-1, 'Config not enabled']
        else:
            self.results['ConfigEnabled'] = [1, 'Config enabled']

    def _checkRecorderStatus(self):
        if self.resource:
            try:
                response = self.client.describe_configuration_recorder_status()
                statuses = response.get('ConfigurationRecordersStatus', [])
                recorder_status = next((s for s in statuses if s['name'] == self.resource['name']), None)
                
                if recorder_status and recorder_status.get('recording'):
                    self.results['RecorderStatus'] = [1, 'Recording active']
                else:
                    self.results['RecorderStatus'] = [-1, 'Recording inactive']
            except ClientError:
                self.results['RecorderStatus'] = [-1, 'Unable to check status']

    def _checkComplianceStatus(self):
        try:
            response = self.client.get_compliance_summary_by_config_rule()
            summary = response.get('ComplianceSummary', {})
            non_compliant = summary.get('NonCompliantResourceCount', {}).get('CappedCount', 0)
            
            if non_compliant > 0:
                self.results['ComplianceStatus'] = [-1, f'{non_compliant} non-compliant resources']
            else:
                self.results['ComplianceStatus'] = [1, 'All resources compliant']
        except ClientError:
            self.results['ComplianceStatus'] = [0, 'Unable to check compliance']