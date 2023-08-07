# coding: utf-8

"""
    JobSet SDK

    Python SDK for the JobSet API  # noqa: E501

    The version of the OpenAPI document: v0.1.4
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

# Kubernetes imports
from kubernetes.client.models.v1_job_template_spec import V1JobTemplateSpec
import unittest
import datetime

import jobset
from jobset.models.jobset_v1alpha2_replicated_job_status import JobsetV1alpha2ReplicatedJobStatus  # noqa: E501
from jobset.rest import ApiException

class TestJobsetV1alpha2ReplicatedJobStatus(unittest.TestCase):
    """JobsetV1alpha2ReplicatedJobStatus unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test JobsetV1alpha2ReplicatedJobStatus
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = jobset.models.jobset_v1alpha2_replicated_job_status.JobsetV1alpha2ReplicatedJobStatus()  # noqa: E501
        if include_optional :
            return JobsetV1alpha2ReplicatedJobStatus(
                active = 56, 
                failed = 56, 
                name = '0', 
                ready = 56, 
                succeeded = 56
            )
        else :
            return JobsetV1alpha2ReplicatedJobStatus(
                active = 56,
                failed = 56,
                name = '0',
                ready = 56,
                succeeded = 56,
        )

    def testJobsetV1alpha2ReplicatedJobStatus(self):
        """Test JobsetV1alpha2ReplicatedJobStatus"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
