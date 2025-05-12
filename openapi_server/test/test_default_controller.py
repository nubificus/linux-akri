import unittest

from flask import json

from openapi_server.models.device_info import DeviceInfo  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.update_request import UpdateRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_info_get(self):
        """Test case for info_get

        Get device information
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/info',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_onboard_get(self):
        """Test case for onboard_get

        Retrieve attestation certificate
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/onboard',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_post(self):
        """Test case for update_post

        Start OTA firmware update
        """
        update_request = {"args":["--ip","192.168.1.100"],"docker_image":"example-updater:latest"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/update',
            method='POST',
            headers=headers,
            data=json.dumps(update_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
