from services.Evaluator import Evaluator

class AccessAnalyzerDriver(Evaluator):
    def __init__(self, analyzer, client):
        super().__init__()
        self.analyzer = analyzer
        self.client = client
        self._resourceName = analyzer['name']
        self.init()

    def _checkAnalyzerStatus(self):
        status = self.analyzer.get('status', 'UNKNOWN')
        if status == 'ACTIVE':
            self.results['AnalyzerStatus'] = [1, 'Active']
        else:
            self.results['AnalyzerStatus'] = [-1, f'Inactive: {status}']

    def _checkAnalyzerType(self):
        analyzer_type = self.analyzer.get('type', 'UNKNOWN')
        if analyzer_type == 'ACCOUNT':
            self.results['AnalyzerType'] = [1, 'Account analyzer']
        elif analyzer_type == 'ORGANIZATION':
            self.results['AnalyzerType'] = [1, 'Organization analyzer']
        else:
            self.results['AnalyzerType'] = [-1, f'Unknown type: {analyzer_type}']

    def _checkActiveFindings(self):
        try:
            response = self.client.list_findings(analyzerArn=self.analyzer['arn'])
            findings = response.get('findings', [])
            active_findings = [f for f in findings if f.get('status') == 'ACTIVE']
            
            if len(active_findings) > 0:
                self.results['ActiveFindings'] = [-1, f'{len(active_findings)} active findings need review']
            else:
                self.results['ActiveFindings'] = [1, 'No active findings']
        except Exception:
            self.results['ActiveFindings'] = [0, 'Unable to check findings']

    def _checkTagging(self):
        tags = self.analyzer.get('tags', {})
        if len(tags) > 0:
            self.results['AnalyzerTagging'] = [1, f'Tagged with {len(tags)} tags']
        else:
            self.results['AnalyzerTagging'] = [-1, 'No tags configured']