"""
This file registers the model with the Python SDK.
"""

from viam.components.generic import Generic
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .camhost import CAMHOST

Registry.register_resource_creator(Generic.SUBTYPE, CAMHOST.MODEL, ResourceCreatorRegistration(CAMHOST.new, CAMHOST.validate))
