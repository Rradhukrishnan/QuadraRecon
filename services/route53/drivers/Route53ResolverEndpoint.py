import botocore
import json
from services.Evaluator import Evaluator

class Route53ResolverEndpoint(Evaluator):
    def __init__(self, endpoint, route53ResolverClient):
        super().__init__()
        self.endpoint = endpoint
        self.route53ResolverClient = route53ResolverClient
        self._resourceName = endpoint['Id']
        self.init()

    def _checkEndpointDirection(self):
        direction = self.endpoint.get('Direction', 'UNKNOWN')
        if direction in ['INBOUND', 'OUTBOUND']:
            self.results['EndpointDirection'] = [1, f'Valid direction: {direction}']
        else:
            self.results['EndpointDirection'] = [-1, f'Invalid direction: {direction}']

    def _checkIPAddressCount(self):
        ip_count = self.endpoint.get('IpAddressCount', 0)
        if ip_count >= 2:
            self.results['IPAddressRedundancy'] = [1, f'Multiple IPs: {ip_count}']
        elif ip_count == 1:
            self.results['IPAddressRedundancy'] = [-1, 'Single IP - no redundancy']
        else:
            self.results['IPAddressRedundancy'] = [-1, 'No IP addresses configured']

    def _checkSecurityGroupConfiguration(self):
        security_groups = self.endpoint.get('SecurityGroupIds', [])
        if len(security_groups) > 0:
            self.results['SecurityGroupAssociation'] = [1, f'Security groups configured: {len(security_groups)}']
        else:
            self.results['SecurityGroupAssociation'] = [-1, 'No security groups configured']

    def _checkEndpointStatus(self):
        status = self.endpoint.get('Status', 'UNKNOWN')
        if status == 'OPERATIONAL':
            self.results['EndpointStatus'] = [1, 'Operational']
        elif status in ['CREATING', 'UPDATING']:
            self.results['EndpointStatus'] = [0, f'In progress: {status}']
        else:
            self.results['EndpointStatus'] = [-1, f'Issue detected: {status}']

    def _checkTagging(self):
        try:
            response = self.route53ResolverClient.list_tags_for_resource(
                ResourceArn=self.endpoint.get('Arn', '')
            )
            tags = response.get('Tags', [])
            if len(tags) > 0:
                self.results['ResolverEndpointTagging'] = [1, f'Tagged with {len(tags)} tags']
            else:
                self.results['ResolverEndpointTagging'] = [-1, 'No tags configured']
        except Exception:
            self.results['ResolverEndpointTagging'] = [0, 'Unable to check tags']

    def _checkCrossAZDeployment(self):
        try:
            # Get IP address details to check AZ distribution
            response = self.route53ResolverClient.list_resolver_endpoint_ip_addresses(
                ResolverEndpointId=self.endpoint['Id']
            )
            ip_addresses = response.get('IpAddresses', [])
            
            subnets = set()
            for ip in ip_addresses:
                subnets.add(ip.get('SubnetId'))
            
            if len(subnets) >= 2:
                self.results['CrossAZDeployment'] = [1, f'Multiple subnets: {len(subnets)}']
            elif len(subnets) == 1:
                self.results['CrossAZDeployment'] = [-1, 'Single subnet - no AZ redundancy']
            else:
                self.results['CrossAZDeployment'] = [-1, 'No subnets configured']
        except Exception:
            self.results['CrossAZDeployment'] = [0, 'Unable to check AZ distribution']