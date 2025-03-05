# coding: utf-8

"""
    JobSet SDK

    Python SDK for the JobSet API

    The version of the OpenAPI document: v0.1.4
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict
from typing import Any, ClassVar, Dict, List, Optional
from jobset.models.io_k8s_api_core_v1_persistent_volume_claim_spec import IoK8sApiCoreV1PersistentVolumeClaimSpec
from jobset.models.io_k8s_apimachinery_pkg_apis_meta_v1_object_meta import IoK8sApimachineryPkgApisMetaV1ObjectMeta
from typing import Optional, Set
from typing_extensions import Self

class IoK8sApiCoreV1PersistentVolumeClaimTemplate(BaseModel):
    """
    PersistentVolumeClaimTemplate is used to produce PersistentVolumeClaim objects as part of an EphemeralVolumeSource.
    """ # noqa: E501
    metadata: Optional[IoK8sApimachineryPkgApisMetaV1ObjectMeta] = None
    spec: IoK8sApiCoreV1PersistentVolumeClaimSpec
    __properties: ClassVar[List[str]] = ["metadata", "spec"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of IoK8sApiCoreV1PersistentVolumeClaimTemplate from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of metadata
        if self.metadata:
            _dict['metadata'] = self.metadata.to_dict()
        # override the default output from pydantic by calling `to_dict()` of spec
        if self.spec:
            _dict['spec'] = self.spec.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IoK8sApiCoreV1PersistentVolumeClaimTemplate from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "metadata": IoK8sApimachineryPkgApisMetaV1ObjectMeta.from_dict(obj["metadata"]) if obj.get("metadata") is not None else None,
            "spec": IoK8sApiCoreV1PersistentVolumeClaimSpec.from_dict(obj["spec"]) if obj.get("spec") is not None else None
        })
        return _obj


