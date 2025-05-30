from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model import Model
from openapi_server import util


class UpdateRequest(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, docker_image=None, args=None):  # noqa: E501
        """UpdateRequest - a model defined in OpenAPI

        :param docker_image: The docker_image of this UpdateRequest.  # noqa: E501
        :type docker_image: str
        :param args: The args of this UpdateRequest.  # noqa: E501
        :type args: List[str]
        """
        self.openapi_types = {
            'docker_image': str,
            'args': List[str]
        }

        self.attribute_map = {
            'docker_image': 'docker_image',
            'args': 'args'
        }

        self._docker_image = docker_image
        self._args = args

    @classmethod
    def from_dict(cls, dikt) -> 'UpdateRequest':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The UpdateRequest of this UpdateRequest.  # noqa: E501
        :rtype: UpdateRequest
        """
        return util.deserialize_model(dikt, cls)

    @property
    def docker_image(self) -> str:
        """Gets the docker_image of this UpdateRequest.


        :return: The docker_image of this UpdateRequest.
        :rtype: str
        """
        return self._docker_image

    @docker_image.setter
    def docker_image(self, docker_image: str):
        """Sets the docker_image of this UpdateRequest.


        :param docker_image: The docker_image of this UpdateRequest.
        :type docker_image: str
        """
        if docker_image is None:
            raise ValueError("Invalid value for `docker_image`, must not be `None`")  # noqa: E501

        self._docker_image = docker_image

    @property
    def args(self) -> List[str]:
        """Gets the args of this UpdateRequest.


        :return: The args of this UpdateRequest.
        :rtype: List[str]
        """
        return self._args

    @args.setter
    def args(self, args: List[str]):
        """Sets the args of this UpdateRequest.


        :param args: The args of this UpdateRequest.
        :type args: List[str]
        """

        self._args = args
