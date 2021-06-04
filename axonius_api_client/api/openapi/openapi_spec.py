# -*- coding: utf-8 -*-
"""API for working with the OpenAPI specification file."""
from ..api_endpoints import ApiEndpoints
from ..models import ApiModel


class OpenAPISpec(ApiModel):
    """API for working with the OpenAPI YAML specification file."""

    def get_spec(self) -> str:
        """Get the OpenAPI specification in YAML format."""
        return self._get_spec()

    def _get_spec(self) -> str:
        """Direct API method to get the OpenAPI YAML specification file."""
        api_endpoint = ApiEndpoints.openapi.get_spec
        return api_endpoint.perform_request(client=self.CLIENT)
