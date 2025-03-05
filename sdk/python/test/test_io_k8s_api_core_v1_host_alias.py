# coding: utf-8

"""
    JobSet SDK

    Python SDK for the JobSet API

    The version of the OpenAPI document: v0.1.4
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from jobset.models.io_k8s_api_core_v1_host_alias import IoK8sApiCoreV1HostAlias

class TestIoK8sApiCoreV1HostAlias(unittest.TestCase):
    """IoK8sApiCoreV1HostAlias unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> IoK8sApiCoreV1HostAlias:
        """Test IoK8sApiCoreV1HostAlias
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `IoK8sApiCoreV1HostAlias`
        """
        model = IoK8sApiCoreV1HostAlias()
        if include_optional:
            return IoK8sApiCoreV1HostAlias(
                hostnames = [
                    ''
                    ],
                ip = ''
            )
        else:
            return IoK8sApiCoreV1HostAlias(
                ip = '',
        )
        """

    def testIoK8sApiCoreV1HostAlias(self):
        """Test IoK8sApiCoreV1HostAlias"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
