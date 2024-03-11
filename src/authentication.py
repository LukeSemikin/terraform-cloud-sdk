from requests import Session

class Authentication:

    def __init__(self, organisation, access_token):
        self.headers = {
            "Content-Type" : "application/vnd.api+json",
            "Authorization": f"Bearer {access_token}"
        }
        self.organisation = organisation
        self.tf_cloud = Session()
        self.tf_cloud.headers.update(self.headers)

    def get_session(self):
        return self.tf_cloud