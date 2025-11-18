import botocore
import json
import time

from utils.Config import Config
from utils.Tools import _pr, _warn
from services.Service import Service
from botocore.config import Config as bConfig

# import drivers here
from services.route53.drivers.Route53HostedZone import Route53HostedZone
from services.route53.drivers.Route53HealthCheck import Route53HealthCheck
from services.route53.drivers.Route53ResolverEndpoint import Route53ResolverEndpoint

from utils.Tools import _pi

class Route53(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        
        ssBoto = self.ssBoto
        self.route53Client = ssBoto.client('route53', config=self.bConfig)
        self.route53ResolverClient = ssBoto.client('route53resolver', config=self.bConfig)
    
    def getResources(self):
        hostedZones = Config.get('route53::hostedZones', [])
        if not hostedZones:
            try:
                results = self.route53Client.list_hosted_zones()
                hostedZones = results.get('HostedZones', [])
                Config.set('route53::hostedZones', hostedZones)
            except botocore.exceptions.ClientError as e:
                ecode = e.response['Error']['Code']
                emsg = e.response['Error']['Message']
                print('route53', ecode, emsg)
                return []
        
        if not self.tags:
            return hostedZones
        
        # Filter by tags if specified
        filteredZones = []
        for zone in hostedZones:
            try:
                result = self.route53Client.list_tags_for_resource(
                    ResourceType='hostedzone',
                    ResourceId=zone['Id'].split('/')[-1]
                )
                tags = result.get('ResourceTagSet', {}).get('Tags', [])
                if self.resourceHasTags(tags):
                    filteredZones.append(zone)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchHostedZone':
                    emsg = e.response['Error']
                    _warn("Route53 Error:({}, {}) is not being handled by Route53::Service".format(emsg['Code'], emsg['Message']))
        
        return filteredZones
    
    def advise(self):
        objs = {}
        
        # Get hosted zones
        hostedZones = self.getResources()
        
        for zone in hostedZones:
            _pi('Route53HostedZone', zone['Name'])
            obj = Route53HostedZone(zone, self.route53Client)
            obj.run(self.__class__)
            objs["HostedZone::" + zone['Name']] = obj.getInfo()
            del obj
        
        # Get health checks (global resource)
        if self.region == 'us-east-1':  # Health checks are global
            try:
                healthChecks = self.route53Client.list_health_checks()
                for hc in healthChecks.get('HealthChecks', []):
                    _pi('Route53HealthCheck', hc['Id'])
                    obj = Route53HealthCheck(hc, self.route53Client)
                    obj.run(self.__class__)
                    objs["HealthCheck::" + hc['Id']] = obj.getInfo()
                    del obj
            except Exception as e:
                print(f"Error processing health checks: {e}")
        
        # Get resolver endpoints
        try:
            resolverEndpoints = self.route53ResolverClient.list_resolver_endpoints()
            for endpoint in resolverEndpoints.get('ResolverEndpoints', []):
                _pi('Route53ResolverEndpoint', endpoint['Id'])
                obj = Route53ResolverEndpoint(endpoint, self.route53ResolverClient)
                obj.run(self.__class__)
                objs["ResolverEndpoint::" + endpoint['Id']] = obj.getInfo()
                del obj
        except Exception as e:
            print(f"Error processing resolver endpoints: {e}")
        
        return objs

if __name__ == "__main__":
    Config.init()
    o = Route53('us-east-1')
    o.advise()