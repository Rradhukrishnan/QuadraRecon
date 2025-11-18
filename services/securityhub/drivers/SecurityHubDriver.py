from services.Evaluator import Evaluator

class SecurityHubDriver(Evaluator):
    def __init__(self, hub, client):
        super().__init__()
        self.hub = hub
        self.client = client
        self._resourceName = 'SecurityHub'
        self.init()

    def _checkHubEnabled(self):
        if not self.hub:
            self.results['HubEnabled'] = [-1, 'Security Hub not enabled']
        else:
            self.results['HubEnabled'] = [1, 'Security Hub enabled']

    def _checkStandardsSubscriptions(self):
        try:
            response = self.client.get_enabled_standards()
            standards = response.get('StandardsSubscriptions', [])
            if len(standards) > 0:
                self.results['StandardsEnabled'] = [1, f'{len(standards)} standards enabled']
            else:
                self.results['StandardsEnabled'] = [-1, 'No security standards enabled']
        except Exception:
            self.results['StandardsEnabled'] = [-1, 'Unable to check standards']

    def _checkActiveFindings(self):
        try:
            response = self.client.get_findings(
                Filters={'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]}
            )
            findings = response.get('Findings', [])
            critical_high = [f for f in findings if f.get('Severity', {}).get('Label') in ['CRITICAL', 'HIGH']]
            
            if len(critical_high) > 0:
                self.results['CriticalFindings'] = [-1, f'{len(critical_high)} critical/high findings']
            else:
                self.results['CriticalFindings'] = [1, 'No critical findings']
        except Exception:
            self.results['CriticalFindings'] = [0, 'Unable to check findings']

    def _checkIntegrations(self):
        try:
            response = self.client.list_enabled_products_for_import()
            integrations = response.get('ProductSubscriptions', [])
            if len(integrations) > 0:
                self.results['SecurityIntegrations'] = [1, f'{len(integrations)} integrations enabled']
            else:
                self.results['SecurityIntegrations'] = [-1, 'No security integrations enabled']
        except Exception:
            self.results['SecurityIntegrations'] = [0, 'Unable to check integrations']

    def _checkInsights(self):
        try:
            response = self.client.get_insights()
            insights = response.get('Insights', [])
            if len(insights) > 0:
                self.results['SecurityInsights'] = [1, f'{len(insights)} insights configured']
            else:
                self.results['SecurityInsights'] = [-1, 'No security insights configured']
        except Exception:
            self.results['SecurityInsights'] = [0, 'Unable to check insights']