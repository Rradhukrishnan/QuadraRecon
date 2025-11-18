from services.Evaluator import Evaluator

class InspectorDriver(Evaluator):
    def __init__(self, resource, client):
        super().__init__()
        self.resource = resource
        self.client = client
        self._resourceName = 'Inspector'
        self.init()

    def _checkInspectorEnabled(self):
        try:
            response = self.client.batch_get_account_status()
            accounts = response.get('accounts', [])
            if accounts and any(acc.get('state', {}).get('status') == 'ENABLED' for acc in accounts):
                self.results['InspectorEnabled'] = [1, 'Inspector enabled']
            else:
                self.results['InspectorEnabled'] = [-1, 'Inspector not enabled']
        except Exception:
            self.results['InspectorEnabled'] = [-1, 'Inspector not available']

    def _checkVulnerabilityFindings(self):
        try:
            response = self.client.list_findings(
                filterCriteria={'severity': [{'comparison': 'EQUALS', 'value': 'HIGH'}]}
            )
            findings = response.get('findings', [])
            if len(findings) > 0:
                self.results['HighSeverityFindings'] = [-1, f'{len(findings)} high severity vulnerabilities']
            else:
                self.results['HighSeverityFindings'] = [1, 'No high severity vulnerabilities']
        except Exception:
            self.results['HighSeverityFindings'] = [0, 'Unable to check findings']

    def _checkCoverageStatus(self):
        try:
            response = self.client.list_coverage()
            coverage = response.get('coveredResources', [])
            if len(coverage) > 0:
                self.results['ResourceCoverage'] = [1, f'{len(coverage)} resources covered']
            else:
                self.results['ResourceCoverage'] = [-1, 'No resources under coverage']
        except Exception:
            self.results['ResourceCoverage'] = [0, 'Unable to check coverage']

    def _checkScanTypes(self):
        try:
            response = self.client.batch_get_account_status()
            accounts = response.get('accounts', [])
            if accounts:
                account = accounts[0]
                ec2_enabled = account.get('resourceState', {}).get('ec2', {}).get('status') == 'ENABLED'
                ecr_enabled = account.get('resourceState', {}).get('ecr', {}).get('status') == 'ENABLED'
                
                enabled_scans = []
                if ec2_enabled:
                    enabled_scans.append('EC2')
                if ecr_enabled:
                    enabled_scans.append('ECR')
                
                if enabled_scans:
                    self.results['ScanTypesEnabled'] = [1, f'Enabled: {", ".join(enabled_scans)}']
                else:
                    self.results['ScanTypesEnabled'] = [-1, 'No scan types enabled']
            else:
                self.results['ScanTypesEnabled'] = [-1, 'Unable to determine scan types']
        except Exception:
            self.results['ScanTypesEnabled'] = [0, 'Unable to check scan types']