from requests import * 
from json import dumps, loads
from src.authentication import Authentication

class Workspaces:

    def __init__(self, organisation, access_token):
        self.organisation = organisation
        self.base_url = "https://app.terraform.io/api/v2/"
        self.auth = Authentication(organisation=organisation, access_token=access_token)
        self.tf_session = self.auth.get_session()

    def workspace_labels(self):
        vcs_labels = [
            "branch",
            "identifier",
            "ingress-submodules",
            "oauth-token-id",
            "tags-regex"
        ]
        settings_labels = [
            "execution-mode"
        ]
        data_labels = [
            "type",
            "id"
        ]
        attributes_labels = [
            "agent-pool-id",
            "allow-destroy-plan",
            "agent-pool-id",
            "auto-apply",
            "auto-apply-run-trigger",
            "auto-destroy-at",
            "auto-destroy-activity-duration",
            "description",
            "execution-mode",
            "file-triggers-enabled",
            "global-remote-state",
            "operation",
            "queue-all-runs",
            "setting-overwrites",
            "source-name",
            "source-url",
            "speculative-enabled",
            "terraform-version",
            "trigger-patterns",
            "trigger-prefixes",
            "working-directory"
        ]
        return vcs_labels, settings_labels, data_labels, attributes_labels
    

    def workspace_validation_set(self, **kwargs):
        vcs_labels, settings_labels, data_labels, attributes_labels = self.workspace_labels()
        all_labels = vcs_labels + settings_labels + data_labels + attributes_labels
        for key, value in kwargs:
            if key not in all_labels:
                print(f"Key: {key} not recognised")
                exit(125)

    def form_data_set(self, name, **kwargs):
        vcs_labels, settings_labels, data_labels, attributes_labels = self.workspace_labels()
        attributes = {
            "name": name
        }
        data = {}
        settings = {}
        vcs = {}
        for key, value in kwargs:
            if key in attributes_labels:
                attributes.update(key, value)
            elif key in data_labels:
                data.update(key, value)
            elif key in vcs_labels:
                vcs.update(key, value)
            elif key in settings_labels:
                settings.update(key, value)
        if settings is not None: 
            attributes.update({"setting-overwrites": settings})
        if vcs is not None: 
            attributes.update({"vcs-repo": vcs})
        payload = {
            "data": {
                "type": "workspace",
                "attributes": attributes
            }
        }
        if data is not None:
            payload.update({"relationships": { "projects": { "data": data } }})
        return dumps(payload)
    
    def form_tags_dataset(self, **tags):
        tags = {}
        for key, value in tags:
            tags.update({
                "type": "tags",
                "attributes": {
                    "name": value
                }
            })
        payload = {
            "data": [
                tags
            ]
        }
        return dumps(payload)

        

#Get Requests

    def list_workspaces(self):
        workspaces = []
        url = f"{self.base_url}organizations/{self.organisation}/workspaces"
        response = self.tf_session.get(url=url)
        for page in range (0, loads(response.content)['meta']['pagination']['total-pages']):
            data = loads(self.tf_session.get(url=url,params={'page':page}).content)['data']
            for workspace in data:
                workspaces.append(workspace)
        return response.status_code, workspaces
    
    def show_workspace(self, workspace_name):
        url = f"{self.base_url}organizations/{self.organisation}/workspaces/{workspace_name}"
        return self.tf_session.get(url=url)
    
    def get_remote_state_consumers(self, workspace_id):
        url = f"{self.base_url}/workspaces/{workspace_id}/relationships/remote-state-consumers"
        return self.tf_session.get(url=url).content
    
    def get_workspace_tags(self, workspace_id):
        url = f"{self.base_url}workspaces/{workspace_id}/relationships/tags"
        return self.get(url=url)
    
#Post Requests
    
    def create_workspace(self, name, **kwargs):
        self.workspace_validation_set()
        payload = self.form_data_set(name, **kwargs)
        url = f"{self.base_url}organizations/{self.organisation}/workspaces"
        self.tf_session.post(data=payload, url=url)

    def safe_delete_workspace(self, identifier, workspace_id):
        if workspace_id == True:
            url = f"{self.base_url}workspaces/{identifier}/actions/safe-delete"
        else:
            url = f"{self.base_url}organizations/{self.organisation}/workspaces/{identifier}/actions/safe-delete"
        self.tf_session.post(url=url)  
    
    def lock_workspace(self, workspace_id, reason):
        url = f"{self.base_url}workspaces/{workspace_id}/actions/lock"
        payload = dumps({
            "reason": reason
        })
        self.tf_session.post(url=url, data=payload)

    def unlock_workspace(self, workspace_id):
        url = f"{self.base_url}workspaces/{workspace_id}/actions/unlock"
        self.tf_session.post(url=url)

    def force_unlock_workspace(self, workspace_id):
        url = f"{self.base_url}workspaces/{workspace_id}/actions/force_unlock"
        self.tf_session.post(url=url)

    def add_remote_state_consumers(self, workspace_id, remote_consumer):
        payload = dumps({
            "data" : [
                {
                    "id": remote_consumer,
                    "type": "workspaces"
                }
            ]
        })
        url = f"{self.base_url}/workspaces/{workspace_id}/relationships/remote-state-consumers"
        return self.tf_session.post(url=url, data=payload)

    def add_tags(self, workspace_id, **tags):
        payload = self.form_tags_dataset(tags)
        url = f"{self.base_url}workspaces/{workspace_id}/relationships/tags"
        self.tf_session.post(url=url, data=payload)

#Patch Requests
    
    def update_workspace(self, name, **kwargs):
        self.workspace_validation_set()
        payload = self.form_data_set(name, **kwargs)
        url = f"{self.base_url}organizations/{self.organisation}/workspaces"
        self.tf_session.patch(data=payload, url=url)

    def assign_ssh_key(self, workspace_id, key_id):
        payload = {
            "data": {
                "attributes": {
                    "id": key_id
                },
                "type": "workspaces"
            }
        }.dumps()
        url = f"{self.base_url}/workspaces/{workspace_id}/relationships/ssh-key"
        self.tf_session.patch(url=url, data=payload)

    def unassign_ssh_key(self, workspace_id):
        self.assign_ssh_key(workspace_id=workspace_id, key_id=None)

    def update_remote_state_consumers(self, workspace_id):
        payload = {
            "data" : [
                {
                    "id": workspace_id,
                    "type": "workspaces"
                }
            ]
        }.dumps()
        url = f"{self.base_url}/workspaces/{workspace_id}/relationships/remote-state-consumers"
        self.tf_session.patch(url=url, data=payload)

        
#Delete Requests
        
    def force_delete_workspace(self, identifier, workspace_id):
        if workspace_id == True:
            url = f"{self.base_url}workspaces/{identifier}/actions/safe-delete"
        else:
            url = f"{self.base_url}organizations/{self.organisation}/workspaces/{identifier}/actions/safe-delete"
        self.tf_session.delete(url=url)

    def delete_remote_state_consumers(self, workspace_id):
        payload = {
            "data" : [
                {
                    "id": workspace_id,
                    "type": "workspaces"
                }
            ]
        }.dumps()
        url = f"{self.base_url}/workspaces/{workspace_id}/relationships/remote-state-consumers"
        self.tf_session.delete(url=url, data=payload)

    def delete_workspace_tags(self, workspace_id, **tags):
        payload = self.form_tags_dataset(tags=tags)
        url = f"{self.base_url}workspaces/{workspace_id}/relationships/tags"
        self.tf_session.delete(url=url, data=payload)