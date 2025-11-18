import botocore
import json
from services.Evaluator import Evaluator

class Route53HostedZone(Evaluator):
    def __init__(self, hostedZone, route53Client):
        super().__init__()
        self.hostedZone = hostedZone
        self.route53Client = route53Client
        self._resourceName = hostedZone['Name']
        self.init()

    def _checkDNSSECEnabled(self):
        try:
            response = self.route53Client.get_dnssec(HostedZoneId=self.hostedZone['Id'])
            status = response.get('StatusList', [])
            if any(s.get('Status') == 'SIGNING' for s in status):
                self.results['DNSSECEnabled'] = [1, 'Enabled']
            else:
                self.results['DNSSECEnabled'] = [-1, 'Disabled']
        except Exception:
            self.results['DNSSECEnabled'] = [-1, 'Not Configured']

    def _checkQueryLoggingEnabled(self):
        try:
            response = self.route53Client.list_query_logging_configs(
                HostedZoneId=self.hostedZone['Id']
            )
            configs = response.get('QueryLoggingConfigs', [])
            if configs:
                self.results['QueryLoggingEnabled'] = [1, 'Enabled']
            else:
                self.results['QueryLoggingEnabled'] = [-1, 'Disabled']
        except Exception:
            self.results['QueryLoggingEnabled'] = [-1, 'Not Available']

    def _checkRecordSetCount(self):
        try:
            response = self.route53Client.list_resource_record_sets(
                HostedZoneId=self.hostedZone['Id']
            )
            recordCount = len(response.get('ResourceRecordSets', []))
            if recordCount > 100:
                self.results['RecordSetCount'] = [-1, f'High count: {recordCount}']
            else:
                self.results['RecordSetCount'] = [1, f'Normal count: {recordCount}']
        except Exception:
            self.results['RecordSetCount'] = [0, 'Unable to check']

    def _checkPrivateZoneVPCAssociation(self):
        if self.hostedZone.get('Config', {}).get('PrivateZone'):
            vpcs = self.hostedZone.get('VPCs', [])
            if len(vpcs) == 0:
                self.results['PrivateZoneVPCAssociation'] = [-1, 'No VPC associations']
            elif len(vpcs) == 1:
                self.results['PrivateZoneVPCAssociation'] = [-1, 'Single VPC - no redundancy']
            else:
                self.results['PrivateZoneVPCAssociation'] = [1, f'Multiple VPCs: {len(vpcs)}']
        else:
            self.results['PrivateZoneVPCAssociation'] = [1, 'Public zone']

    def _checkAliasRecords(self):
        try:
            response = self.route53Client.list_resource_record_sets(
                HostedZoneId=self.hostedZone['Id']
            )
            records = response.get('ResourceRecordSets', [])
            aliasCount = sum(1 for r in records if r.get('AliasTarget'))
            totalRecords = len(records)
            
            if totalRecords > 0:
                aliasRatio = aliasCount / totalRecords
                if aliasRatio > 0.5:
                    self.results['AliasRecordUsage'] = [1, f'Good alias usage: {aliasCount}/{totalRecords}']
                else:
                    self.results['AliasRecordUsage'] = [-1, f'Low alias usage: {aliasCount}/{totalRecords}']
            else:
                self.results['AliasRecordUsage'] = [0, 'No records found']
        except Exception:
            self.results['AliasRecordUsage'] = [0, 'Unable to check']

    def _checkHealthCheckAssociation(self):
        try:
            response = self.route53Client.list_resource_record_sets(
                HostedZoneId=self.hostedZone['Id']
            )
            records = response.get('ResourceRecordSets', [])
            healthCheckCount = sum(1 for r in records if r.get('HealthCheckId'))
            
            if healthCheckCount > 0:
                self.results['HealthCheckAssociation'] = [1, f'Health checks configured: {healthCheckCount}']
            else:
                self.results['HealthCheckAssociation'] = [-1, 'No health checks configured']
        except Exception:
            self.results['HealthCheckAssociation'] = [0, 'Unable to check']