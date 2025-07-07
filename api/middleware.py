import hashlib
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from database.connection import get_pool


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using SHA-256.
    
    Parameters
    ----------
    api_key : str
        The plain text API key to hash.
        
    Returns
    -------
    str
        The SHA-256 hash of the API key.
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


async def validate_api_key(api_key: str, organization_id: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate an API key for a specific organization.
    
    Parameters
    ----------
    api_key : str
        The API key to validate (can be plain text or hash).
        
    organization_id : str
        The UUID of the organization to validate against.
        
    Returns
    -------
    Tuple[bool, str, Optional[str]]
        A tuple containing:
        - bool: True if validation successful, False otherwise
        - str: Organization name if successful, error message if failed
        - Optional[str]: None if successful, detailed error if failed
    """
    try:
        pool = await get_pool()
        if pool is None:
            return False, "Database connection pool is not available", None

        # First, check if organization exists
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT organization_name
                FROM clients 
                WHERE id = $1
            """, organization_id)

        if row is None:
            return False, f"Organization '{organization_id}' is not enrolled", None
        
        organization_name = row["organization_name"]

        # Get the stored API key hash and active status
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT api_key, is_active
                FROM api_keys
                WHERE client_id = $1
            """, organization_id)

        if row is None:
            return False, f"Organization '{organization_name}' has no API key configured", None

        stored_api_key_hash = row["api_key"]
        is_active = row["is_active"]

        if not is_active:
            return False, f"Organization '{organization_name}' is not active", None

        # Check if the provided API key matches (handle both plain text and hash)
        provided_hash = hash_api_key(api_key)
        
        if provided_hash != stored_api_key_hash:
            return False, f"Invalid API key for organization '{organization_name}'", None

        # Update last_used timestamp
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE api_keys 
                SET last_used = CURRENT_TIMESTAMP
                WHERE client_id = $1
            """, organization_id)

        return True, organization_name, None

    except Exception as e:
        return False, f"Internal server error during API key validation: {str(e)}", None


async def api_key_middleware(request: Request, call_next):
    """
    FastAPI middleware to validate API keys for protected endpoints.
    
    This middleware intercepts requests to protected endpoints and validates
    the API key before allowing the request to proceed. It checks the
    X-API-Key header and validates it against the organization's stored
    API key hash.
    
    Parameters
    ----------
    request : Request
        The incoming FastAPI request object.
        
    call_next : Callable
        The next middleware or endpoint handler in the chain.
        
    Returns
    -------
    Response
        The response from the endpoint if validation passes, or an error
        response if validation fails.
        
    Notes
    -----
    - Only applies to endpoints that require API key authentication
    - Expects X-API-Key header with the API key
    - Expects organization_id in form data or query parameters
    - Automatically updates last_used timestamp for valid API keys
    - Returns standardized error responses for validation failures
    """
    # List of endpoints that require API key authentication
    protected_endpoints = [
        "/api/enroll_camera", 
        "/api/enroll_identity",
        "/api/enroll_refrence_iamge",
        "/api/identify"
    ]
    
    # Check if this is a protected endpoint
    if request.url.path in protected_endpoints:
        try:
            # Get API key from header
            api_key = request.headers.get("x-api-key")
            if not api_key:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": "error",
                        "message": "API key is required. Please provide x-api-key header."
                    }
                )
            
            # Get organization_id from form data or query params
            organization_id = None

            try:
                organization_id = request.headers.get("x-organization-id")
            except:
                print("No organization_id in form data")
                pass
            
            if not organization_id:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "organization_id is required in form data or query parameters."
                    }
                )
            
            # Validate the API key
            is_valid, result, error = await validate_api_key(api_key, organization_id)
            
            if not is_valid:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": "error",
                        "message": result
                    }
                )
            
            # Add organization name to request state for use in endpoints
            request.state.organization_name = result
            
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": f"Internal server error during authentication: {str(e)}"
                }
            )
    
    # Continue to the next middleware or endpoint
    response = await call_next(request)
    return response 