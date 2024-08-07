# coding: utf-8

"""
    JobSet SDK

    Python SDK for the JobSet API  # noqa: E501

    The version of the OpenAPI document: v0.1.4
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from jobset.configuration import Configuration


class JobsetV1alpha2JobSetSpec(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'coordinator': 'JobsetV1alpha2Coordinator',
        'failure_policy': 'JobsetV1alpha2FailurePolicy',
        'managed_by': 'str',
        'network': 'JobsetV1alpha2Network',
        'replicated_jobs': 'list[JobsetV1alpha2ReplicatedJob]',
        'startup_policy': 'JobsetV1alpha2StartupPolicy',
        'success_policy': 'JobsetV1alpha2SuccessPolicy',
        'suspend': 'bool',
        'ttl_seconds_after_finished': 'int'
    }

    attribute_map = {
        'coordinator': 'coordinator',
        'failure_policy': 'failurePolicy',
        'managed_by': 'managedBy',
        'network': 'network',
        'replicated_jobs': 'replicatedJobs',
        'startup_policy': 'startupPolicy',
        'success_policy': 'successPolicy',
        'suspend': 'suspend',
        'ttl_seconds_after_finished': 'ttlSecondsAfterFinished'
    }

    def __init__(self, coordinator=None, failure_policy=None, managed_by=None, network=None, replicated_jobs=None, startup_policy=None, success_policy=None, suspend=None, ttl_seconds_after_finished=None, local_vars_configuration=None):  # noqa: E501
        """JobsetV1alpha2JobSetSpec - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._coordinator = None
        self._failure_policy = None
        self._managed_by = None
        self._network = None
        self._replicated_jobs = None
        self._startup_policy = None
        self._success_policy = None
        self._suspend = None
        self._ttl_seconds_after_finished = None
        self.discriminator = None

        if coordinator is not None:
            self.coordinator = coordinator
        if failure_policy is not None:
            self.failure_policy = failure_policy
        if managed_by is not None:
            self.managed_by = managed_by
        if network is not None:
            self.network = network
        if replicated_jobs is not None:
            self.replicated_jobs = replicated_jobs
        if startup_policy is not None:
            self.startup_policy = startup_policy
        if success_policy is not None:
            self.success_policy = success_policy
        if suspend is not None:
            self.suspend = suspend
        if ttl_seconds_after_finished is not None:
            self.ttl_seconds_after_finished = ttl_seconds_after_finished

    @property
    def coordinator(self):
        """Gets the coordinator of this JobsetV1alpha2JobSetSpec.  # noqa: E501


        :return: The coordinator of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: JobsetV1alpha2Coordinator
        """
        return self._coordinator

    @coordinator.setter
    def coordinator(self, coordinator):
        """Sets the coordinator of this JobsetV1alpha2JobSetSpec.


        :param coordinator: The coordinator of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: JobsetV1alpha2Coordinator
        """

        self._coordinator = coordinator

    @property
    def failure_policy(self):
        """Gets the failure_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501


        :return: The failure_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: JobsetV1alpha2FailurePolicy
        """
        return self._failure_policy

    @failure_policy.setter
    def failure_policy(self, failure_policy):
        """Sets the failure_policy of this JobsetV1alpha2JobSetSpec.


        :param failure_policy: The failure_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: JobsetV1alpha2FailurePolicy
        """

        self._failure_policy = failure_policy

    @property
    def managed_by(self):
        """Gets the managed_by of this JobsetV1alpha2JobSetSpec.  # noqa: E501

        ManagedBy is used to indicate the controller or entity that manages a JobSet. The built-in JobSet controller reconciles JobSets which don't have this field at all or the field value is the reserved string `jobset.sigs.k8s.io/jobset-controller`, but skips reconciling JobSets with a custom value for this field.  The value must be a valid domain-prefixed path (e.g. acme.io/foo) - all characters before the first \"/\" must be a valid subdomain as defined by RFC 1123. All characters trailing the first \"/\" must be valid HTTP Path characters as defined by RFC 3986. The value cannot exceed 63 characters. The field is immutable.  # noqa: E501

        :return: The managed_by of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: str
        """
        return self._managed_by

    @managed_by.setter
    def managed_by(self, managed_by):
        """Sets the managed_by of this JobsetV1alpha2JobSetSpec.

        ManagedBy is used to indicate the controller or entity that manages a JobSet. The built-in JobSet controller reconciles JobSets which don't have this field at all or the field value is the reserved string `jobset.sigs.k8s.io/jobset-controller`, but skips reconciling JobSets with a custom value for this field.  The value must be a valid domain-prefixed path (e.g. acme.io/foo) - all characters before the first \"/\" must be a valid subdomain as defined by RFC 1123. All characters trailing the first \"/\" must be valid HTTP Path characters as defined by RFC 3986. The value cannot exceed 63 characters. The field is immutable.  # noqa: E501

        :param managed_by: The managed_by of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: str
        """

        self._managed_by = managed_by

    @property
    def network(self):
        """Gets the network of this JobsetV1alpha2JobSetSpec.  # noqa: E501


        :return: The network of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: JobsetV1alpha2Network
        """
        return self._network

    @network.setter
    def network(self, network):
        """Sets the network of this JobsetV1alpha2JobSetSpec.


        :param network: The network of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: JobsetV1alpha2Network
        """

        self._network = network

    @property
    def replicated_jobs(self):
        """Gets the replicated_jobs of this JobsetV1alpha2JobSetSpec.  # noqa: E501

        ReplicatedJobs is the group of jobs that will form the set.  # noqa: E501

        :return: The replicated_jobs of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: list[JobsetV1alpha2ReplicatedJob]
        """
        return self._replicated_jobs

    @replicated_jobs.setter
    def replicated_jobs(self, replicated_jobs):
        """Sets the replicated_jobs of this JobsetV1alpha2JobSetSpec.

        ReplicatedJobs is the group of jobs that will form the set.  # noqa: E501

        :param replicated_jobs: The replicated_jobs of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: list[JobsetV1alpha2ReplicatedJob]
        """

        self._replicated_jobs = replicated_jobs

    @property
    def startup_policy(self):
        """Gets the startup_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501


        :return: The startup_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: JobsetV1alpha2StartupPolicy
        """
        return self._startup_policy

    @startup_policy.setter
    def startup_policy(self, startup_policy):
        """Sets the startup_policy of this JobsetV1alpha2JobSetSpec.


        :param startup_policy: The startup_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: JobsetV1alpha2StartupPolicy
        """

        self._startup_policy = startup_policy

    @property
    def success_policy(self):
        """Gets the success_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501


        :return: The success_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: JobsetV1alpha2SuccessPolicy
        """
        return self._success_policy

    @success_policy.setter
    def success_policy(self, success_policy):
        """Sets the success_policy of this JobsetV1alpha2JobSetSpec.


        :param success_policy: The success_policy of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: JobsetV1alpha2SuccessPolicy
        """

        self._success_policy = success_policy

    @property
    def suspend(self):
        """Gets the suspend of this JobsetV1alpha2JobSetSpec.  # noqa: E501

        Suspend suspends all running child Jobs when set to true.  # noqa: E501

        :return: The suspend of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: bool
        """
        return self._suspend

    @suspend.setter
    def suspend(self, suspend):
        """Sets the suspend of this JobsetV1alpha2JobSetSpec.

        Suspend suspends all running child Jobs when set to true.  # noqa: E501

        :param suspend: The suspend of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: bool
        """

        self._suspend = suspend

    @property
    def ttl_seconds_after_finished(self):
        """Gets the ttl_seconds_after_finished of this JobsetV1alpha2JobSetSpec.  # noqa: E501

        TTLSecondsAfterFinished limits the lifetime of a JobSet that has finished execution (either Complete or Failed). If this field is set, TTLSecondsAfterFinished after the JobSet finishes, it is eligible to be automatically deleted. When the JobSet is being deleted, its lifecycle guarantees (e.g. finalizers) will be honored. If this field is unset, the JobSet won't be automatically deleted. If this field is set to zero, the JobSet becomes eligible to be deleted immediately after it finishes.  # noqa: E501

        :return: The ttl_seconds_after_finished of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :rtype: int
        """
        return self._ttl_seconds_after_finished

    @ttl_seconds_after_finished.setter
    def ttl_seconds_after_finished(self, ttl_seconds_after_finished):
        """Sets the ttl_seconds_after_finished of this JobsetV1alpha2JobSetSpec.

        TTLSecondsAfterFinished limits the lifetime of a JobSet that has finished execution (either Complete or Failed). If this field is set, TTLSecondsAfterFinished after the JobSet finishes, it is eligible to be automatically deleted. When the JobSet is being deleted, its lifecycle guarantees (e.g. finalizers) will be honored. If this field is unset, the JobSet won't be automatically deleted. If this field is set to zero, the JobSet becomes eligible to be deleted immediately after it finishes.  # noqa: E501

        :param ttl_seconds_after_finished: The ttl_seconds_after_finished of this JobsetV1alpha2JobSetSpec.  # noqa: E501
        :type: int
        """

        self._ttl_seconds_after_finished = ttl_seconds_after_finished

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, JobsetV1alpha2JobSetSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, JobsetV1alpha2JobSetSpec):
            return True

        return self.to_dict() != other.to_dict()
