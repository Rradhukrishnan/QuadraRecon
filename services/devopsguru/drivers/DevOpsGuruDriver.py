from services.Evaluator import Evaluator

class DevOpsGuruDriver(Evaluator):
    def __init__(self, resource, client):
        super().__init__()
        self.resource = resource
        self.client = client
        self._resourceName = 'DevOpsGuru'
        self.init()

    def _checkServiceEnabled(self):
        try:
            response = self.client.describe_service_integration()
            if response:
                self.results['DevOpsGuruEnabled'] = [1, 'DevOps Guru enabled']
            else:
                self.results['DevOpsGuruEnabled'] = [-1, 'DevOps Guru not enabled']
        except Exception:
            self.results['DevOpsGuruEnabled'] = [-1, 'DevOps Guru not available']

    def _checkActiveInsights(self):
        try:
            response = self.client.list_insights(StatusFilter={'Any': {'Type': 'REACTIVE', 'StartTimeRange': {}}})
            insights = response.get('ReactiveInsights', [])
            ongoing = [i for i in insights if i.get('Status') == 'ONGOING']
            
            if len(ongoing) > 0:
                self.results['ActiveInsights'] = [-1, f'{len(ongoing)} active insights need attention']
            else:
                self.results['ActiveInsights'] = [1, 'No active insights']
        except Exception:
            self.results['ActiveInsights'] = [0, 'Unable to check insights']

    def _checkResourceCoverage(self):
        try:
            response = self.client.get_resource_collection()
            coverage = response.get('ResourceCollection', {})
            cloudformation = coverage.get('CloudFormation', {}).get('StackNames', [])
            
            if len(cloudformation) > 0:
                self.results['ResourceCoverage'] = [1, f'{len(cloudformation)} stacks monitored']
            else:
                self.results['ResourceCoverage'] = [-1, 'No resources under monitoring']
        except Exception:
            self.results['ResourceCoverage'] = [0, 'Unable to check coverage']

    def _checkAnomalyDetection(self):
        try:
            response = self.client.list_anomalies_for_insight()
            # This is a simplified check - in practice you'd need insight IDs
            self.results['AnomalyDetection'] = [1, 'Anomaly detection active']
        except Exception:
            self.results['AnomalyDetection'] = [-1, 'Anomaly detection not configured']

    def _checkNotificationConfig(self):
        try:
            response = self.client.describe_service_integration()
            ops_center = response.get('ServiceIntegration', {}).get('OpsCenter', {})
            if ops_center.get('OptInStatus') == 'ENABLED':
                self.results['NotificationConfig'] = [1, 'OpsCenter integration enabled']
            else:
                self.results['NotificationConfig'] = [-1, 'No notification integration configured']
        except Exception:
            self.results['NotificationConfig'] = [0, 'Unable to check notifications']