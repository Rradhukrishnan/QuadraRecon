import botocore
import json
from services.Evaluator import Evaluator

class Route53HealthCheck(Evaluator):
    def __init__(self, healthCheck, route53Client):
        super().__init__()
        self.healthCheck = healthCheck
        self.route53Client = route53Client
        self._resourceName = healthCheck['Id']
        self.init()

    def _checkHealthCheckStatus(self):
        try:
            response = self.route53Client.get_health_check_status(
                HealthCheckId=self.healthCheck['Id']
            )
            checkers = response.get('CheckerIpRanges', [])
            if len(checkers) >= 3:
                self.results['HealthCheckRedundancy'] = [1, f'Multiple checkers: {len(checkers)}']
            else:
                self.results['HealthCheckRedundancy'] = [-1, f'Few checkers: {len(checkers)}']
        except Exception:
            self.results['HealthCheckRedundancy'] = [0, 'Unable to check status']

    def _checkHealthCheckType(self):
        hc_type = self.healthCheck.get('Type', 'UNKNOWN')
        if hc_type in ['HTTP', 'HTTPS', 'TCP']:
            self.results['HealthCheckType'] = [1, f'Standard type: {hc_type}']
        elif hc_type == 'CALCULATED':
            self.results['HealthCheckType'] = [1, 'Calculated health check']
        else:
            self.results['HealthCheckType'] = [-1, f'Unusual type: {hc_type}']

    def _checkHealthCheckInterval(self):
        interval = self.healthCheck.get('HealthCheckConfig', {}).get('RequestInterval', 30)
        if interval <= 10:
            self.results['HealthCheckInterval'] = [-1, f'Very frequent: {interval}s - may increase costs']
        elif interval <= 30:
            self.results['HealthCheckInterval'] = [1, f'Standard interval: {interval}s']
        else:
            self.results['HealthCheckInterval'] = [-1, f'Long interval: {interval}s - may delay failover']

    def _checkFailureThreshold(self):
        threshold = self.healthCheck.get('HealthCheckConfig', {}).get('FailureThreshold', 3)
        if threshold < 2:
            self.results['FailureThreshold'] = [-1, f'Too sensitive: {threshold}']
        elif threshold <= 3:
            self.results['FailureThreshold'] = [1, f'Appropriate: {threshold}']
        else:
            self.results['FailureThreshold'] = [-1, f'Too tolerant: {threshold}']

    def _checkCloudWatchAlarmIntegration(self):
        config = self.healthCheck.get('HealthCheckConfig', {})
        if config.get('AlarmRegion') and config.get('AlarmName'):
            self.results['CloudWatchIntegration'] = [1, 'CloudWatch alarm configured']
        else:
            self.results['CloudWatchIntegration'] = [-1, 'No CloudWatch alarm integration']

    def _checkTagging(self):
        try:
            response = self.route53Client.list_tags_for_resource(
                ResourceType='healthcheck',
                ResourceId=self.healthCheck['Id']
            )
            tags = response.get('ResourceTagSet', {}).get('Tags', [])
            if len(tags) > 0:
                self.results['HealthCheckTagging'] = [1, f'Tagged with {len(tags)} tags']
            else:
                self.results['HealthCheckTagging'] = [-1, 'No tags configured']
        except Exception:
            self.results['HealthCheckTagging'] = [0, 'Unable to check tags']