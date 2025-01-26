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

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from jobset.models.jobset_v1alpha2_failure_policy_rule import JobsetV1alpha2FailurePolicyRule
from typing import Optional, Set
from typing_extensions import Self

class JobsetV1alpha2FailurePolicy(BaseModel):
    """
    JobsetV1alpha2FailurePolicy
    """ # noqa: E501
    max_restarts: Optional[StrictInt] = Field(default=None, description="MaxRestarts defines the limit on the number of JobSet restarts. A restart is achieved by recreating all active child jobs.", alias="maxRestarts")
    restart_strategy: Optional[StrictStr] = Field(default=None, description="RestartStrategy defines the strategy to use when restarting the JobSet. Defaults to Recreate.", alias="restartStrategy")
    rules: Optional[List[JobsetV1alpha2FailurePolicyRule]] = Field(default=None, description="List of failure policy rules for this JobSet. For a given Job failure, the rules will be evaluated in order, and only the first matching rule will be executed. If no matching rule is found, the RestartJobSet action is applied.")
    __properties: ClassVar[List[str]] = ["maxRestarts", "restartStrategy", "rules"]

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
        """Create an instance of JobsetV1alpha2FailurePolicy from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in rules (list)
        _items = []
        if self.rules:
            for _item_rules in self.rules:
                if _item_rules:
                    _items.append(_item_rules.to_dict())
            _dict['rules'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of JobsetV1alpha2FailurePolicy from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "maxRestarts": obj.get("maxRestarts"),
            "restartStrategy": obj.get("restartStrategy"),
            "rules": [JobsetV1alpha2FailurePolicyRule.from_dict(_item) for _item in obj["rules"]] if obj.get("rules") is not None else None
        })
        return _obj


