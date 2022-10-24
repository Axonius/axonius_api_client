# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import copy
import dataclasses
import logging
from typing import List, Optional

from .data import BaseData
from .setup_env import KEY_FEATURES, get_env_features

PRODUCT_ABOUT: dict = {}
LOGGER = logging.getLogger("axonius_api_client.features")


@dataclasses.dataclass
class FeatureEnabled(BaseData):  # pragma: no cover
    """Pass."""

    result: bool
    feature: "Feature"
    env_features: List[str]
    product_about: dict
    reason: str

    def __post_init__(self):
        """Pass."""
        LOGGER.debug(f"{self}")

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"FEATURE CHECK {self.feature.name}",
            f"OS Environment Variable {KEY_FEATURES!r}: {self.env_features}",
            f"Product about: {self.product_about}",
            f"Feature enabled: {self.result}",
            f"Reason: {self.reason}",
        ]
        return "\n".join(items)

    def __repr__(self):
        """Pass."""
        return self.__str__()


@dataclasses.dataclass
class Feature(BaseData):  # pragma: no cover
    """Pass."""

    name: str
    description: str
    version_client_added: str = ""
    version_product_min: str = ""
    version_empty: bool = False
    product_ticket: str = ""
    force: bool = False

    def check_enabled(self, about: Optional[dict] = None) -> FeatureEnabled:
        """Pass."""
        about = copy.deepcopy(about or PRODUCT_ABOUT)
        env_features = get_env_features()
        min_ver = self.version_product_min
        prod_ver = about.get("Version")
        fe_kwargs = {
            "feature": self,
            "env_features": env_features,
            "product_about": PRODUCT_ABOUT,
        }

        if self.force:
            reason = f"force is {self.force}"
            return FeatureEnabled(result=True, reason=reason, **fe_kwargs)

        if f"no_{self.name}" in env_features:
            reason = f"disabled in OS environment variable {KEY_FEATURES!r}"
            return FeatureEnabled(result=False, reason=reason, **fe_kwargs)

        if self.name in env_features:
            reason = f"enabled in OS environment variable {KEY_FEATURES!r}"
            return FeatureEnabled(result=True, reason=reason, **fe_kwargs)

        if not min_ver:
            reason = f"minimum product version is empty: {min_ver!r}"
            return FeatureEnabled(result=True, reason=reason, **fe_kwargs)

        if not prod_ver:
            reason = (
                f"Axonius version is empty: {prod_ver!r} and version_empty is {self.version_empty}"
            )
            if self.version_empty:
                return FeatureEnabled(result=True, reason=reason, **fe_kwargs)
            else:
                return FeatureEnabled(result=False, reason=reason, **fe_kwargs)

        if prod_ver >= min_ver:
            reason = f"Axonius version {prod_ver!r} >= Feature version {min_ver!r}"
            return FeatureEnabled(result=True, reason=reason, **fe_kwargs)

        reason = f"Axonius version {prod_ver!r} not >= Feature version {min_ver!r}"
        return FeatureEnabled(result=False, reason=reason, **fe_kwargs)

    def __str__(self) -> str:
        """Pass."""
        vmin = self.version_product_min
        vadd = self.version_client_added
        name = self.name
        items = [
            f"Feature name: {name} - Added in API client version: {vadd!r}",
            f"Enabled if Axonius product version is greater than or equal to: {vmin}",
            f"Enable in .env by adding a line:\nAX_FEATURES={name}\n",
            f"Enable in Unix shell via:\nexport AX_FEATURES={name}\n",
            f"Enable in Windows CMD via:\nset AX_FEATURES={name}\n",
            f"Enable in python via:\naxonius_api_client.features.Features.{name}.force = True\n",
            f"Enable in python via:\nimport os; os.environ['AX_FEATURES'] = '{name}'\n",
            f"Description:{self.description}",
        ]
        return "\n# " + "\n# ".join(items)

    def __repr__(self):
        """Pass."""
        return self.__str__()


@dataclasses.dataclass
class Features(BaseData):  # pragma: no cover
    """Pass."""

    @classmethod
    def get_features(cls) -> List[Feature]:
        """Pass."""
        return [x.default for x in cls.get_fields()]

    # built into product as of 4.4
    '''
    raw_data: Feature = Feature(
        name="raw_data",
        version_product_min="4.4",
        version_client_added="4.10.6",
        product_ticket="AX-13595",
        description="""
- Adds ability to get aggregated raw data in API library via:
client.devices.get(fields=['agg:raw_data'])
client.users.get(fields=['agg:raw_data'])

- Adds ability to get aggregated raw data in CLI via:
axonshell devices get --field agg:raw_data
axonshell users get --field agg:raw_data

- Adds ability to get adapter specific raw data in API library via:
client.devices.get(fields=['aws:raw_data'])
client.users.get(fields=['aws:raw_data'])

- Adds ability to get adapter specific raw data in CLI via:
axonshell devices get --field aws:raw_data
axonshell users get --field aws:raw_data

""",
    )
    '''
