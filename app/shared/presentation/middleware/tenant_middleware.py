"""
Tenant isolation middleware for multi-tenant architecture.
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to handle tenant context and isolation."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and set tenant context."""
        
        # Extract tenant ID from various sources
        tenant_id = None
        
        # 1. Check subdomain (e.g., tenant1.elevate.com)
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain not in ["www", "api", "admin"]:
                tenant_id = subdomain
        
        # 2. Check custom header
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")
        
        # 3. Check query parameter (for development)
        if not tenant_id:
            tenant_id = request.query_params.get("tenant_id")
        
        # 4. Extract from path (e.g., /api/v1/tenants/{tenant_id}/...)
        if not tenant_id and request.url.path.startswith("/api/v1/tenants/"):
            path_parts = request.url.path.split("/")
            if len(path_parts) > 4:
                tenant_id = path_parts[4]
        
        # Set tenant context in request state
        request.state.tenant_id = tenant_id
        
        # Process request
        response = await call_next(request)
        
        # Add tenant ID to response headers (optional, for debugging)
        if tenant_id:
            response.headers["X-Tenant-ID"] = tenant_id
        
        return response
