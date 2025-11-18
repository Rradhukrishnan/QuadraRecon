from services.Evaluator import Evaluator

class SSMDriver(Evaluator):
    def __init__(self, resource, client):
        super().__init__()
        self.resource = resource
        self.client = client
        self._resourceName = 'SystemsManager'
        self.init()

    def _checkManagedInstances(self):
        try:
            response = self.client.describe_instance_information()
            instances = response.get('InstanceInformationList', [])
            if len(instances) > 0:
                self.results['ManagedInstances'] = [1, f'{len(instances)} managed instances']
            else:
                self.results['ManagedInstances'] = [-1, 'No managed instances']
        except Exception:
            self.results['ManagedInstances'] = [0, 'Unable to check managed instances']

    def _checkPatchCompliance(self):
        try:
            response = self.client.describe_instance_patch_states()
            patch_states = response.get('InstancePatchStates', [])
            non_compliant = [p for p in patch_states if p.get('Operation') != 'Install']
            
            if len(non_compliant) > 0:
                self.results['PatchCompliance'] = [-1, f'{len(non_compliant)} instances need patches']
            else:
                self.results['PatchCompliance'] = [1, 'All instances patch compliant']
        except Exception:
            self.results['PatchCompliance'] = [0, 'Unable to check patch compliance']

    def _checkMaintenanceWindows(self):
        try:
            response = self.client.describe_maintenance_windows()
            windows = response.get('WindowIdentities', [])
            if len(windows) > 0:
                self.results['MaintenanceWindows'] = [1, f'{len(windows)} maintenance windows configured']
            else:
                self.results['MaintenanceWindows'] = [-1, 'No maintenance windows configured']
        except Exception:
            self.results['MaintenanceWindows'] = [0, 'Unable to check maintenance windows']

    def _checkParameterStore(self):
        try:
            response = self.client.describe_parameters()
            parameters = response.get('Parameters', [])
            secure_params = [p for p in parameters if p.get('Type') == 'SecureString']
            
            if len(parameters) > 0:
                self.results['ParameterStore'] = [1, f'{len(parameters)} parameters ({len(secure_params)} secure)']
            else:
                self.results['ParameterStore'] = [-1, 'No parameters in Parameter Store']
        except Exception:
            self.results['ParameterStore'] = [0, 'Unable to check Parameter Store']

    def _checkSessionManager(self):
        try:
            response = self.client.describe_sessions(State='Active')
            sessions = response.get('Sessions', [])
            # Check if Session Manager is configured by looking for preferences
            prefs_response = self.client.get_document(Name='SSM-SessionManagerRunShell')
            
            if prefs_response:
                self.results['SessionManager'] = [1, 'Session Manager configured']
            else:
                self.results['SessionManager'] = [-1, 'Session Manager not configured']
        except Exception:
            self.results['SessionManager'] = [-1, 'Session Manager not available']