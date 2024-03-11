from src.workspaces import Workspaces
from os import environ
from unittest import main, TestCase
from json import loads


class TestWorkspaces(TestCase):

    runner = Workspaces("luke_semikin", environ['tf_access_token'])
    test_workspace_name = "dummy_workspace"

    def test_create_workspace(self):
        self.runner.create_workspace(self.test_workspace_name)
        response = self.runner.show_workspace(self.test_workspace_name)
        self.assertEqual(200, response.status_code)

    def test_list_workspaces_response(self):
        response, workspaces = self.runner.list_workspaces()
        self.assertEqual(200, response)

    def test_list_workspace_name(self):
        response, workspaces = self.runner.list_workspaces()
        for workspace in workspaces:
            if workspace['attributes']['name'] == self.test_workspace_name:
                break
        self.assertEqual(workspace['attributes']['name'],self.test_workspace_name)

    def test_show_workspace_response(self):
        response = self.runner.show_workspace(self.test_workspace_name).status_code
        self.assertEqual(200, response)

    def test_show_workspace_name(self):
        workspace = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']
        self.assertEqual(workspace['attributes']['name'],self.test_workspace_name)

    def test_lock_workspace(self):
        workspace_id = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['id']
        self.runner.lock_workspace(workspace_id, "Test Lock")
        self.assertTrue(loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['attributes']['locked'])

    def test_unlock_workspace(self):
        workspace_id = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['id']
        self.runner.unlock_workspace(workspace_id)
        self.assertFalse(loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['attributes']['locked'])

    def test_add_remote_state_consumers(self):
        self.runner.create_workspace(f"{self.test_workspace_name}-rsc")
        workspace_id = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['id']
        rsc_workspace_id = loads(self.runner.show_workspace(f"{self.test_workspace_name}-rsc").content)['data']['id']
        self.assertEqual(204, self.runner.add_remote_state_consumers(workspace_id, rsc_workspace_id).status_code)

    def test_get_remote_state_consumers(self):
        workspace_id = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['id']
        rsc_workspace_id = loads(self.runner.show_workspace(f"{self.test_workspace_name}-rsc").content)['data']['id']
        self.runner.add_remote_state_consumers(workspace_id, rsc_workspace_id)
        response = loads(self.runner.get_remote_state_consumers(workspace_id))
        self.assertEqual(f"{self.test_workspace_name}-rsc", response['data'][0]['attributes']['name'])

    def test_update_remote_state_consumers(self):
        self.runner.create_workspace(f"{self.test_workspace_name}-rsc")
        workspace_id = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['id']
        rsc_workspace_id = loads(self.runner.show_workspace(f"{self.test_workspace_name}-rsc").content)['data']['id']
        self.runner.add_remote_state_consumers(workspace_id, rsc_workspace_id)
        self.assertEqual(204, self.runner.update_remote_state_consumers(workspace_id, rsc_workspace_id))

    def test_delete_remote_state_consumers(self):
        self.runner.create_workspace(f"{self.test_workspace_name}-rsc")
        workspace_id = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['id']
        rsc_workspace_id = loads(self.runner.show_workspace(f"{self.test_workspace_name}-rsc").content)['data']['id']
        self.assertEqual(204, self.runner.delete_remote_state_consumers(workspace_id, rsc_workspace_id))
       
    def add_tags(self):

    # def test_force_unlock_workspace(self):
    #     workspace_id = loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['id']
    #     self.runner.lock_workspace(workspace_id, "Test Lock")
    #     self.runner.force_unlock_workspace(workspace_id)
    #     self.assertFalse(loads(self.runner.show_workspace(self.test_workspace_name).content)['data']['attributes']['locked'])

if __name__ == '__main__':
    testsuite = main()
