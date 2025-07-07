from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


def get_organization_name_from_request(request: Request) -> str:
    """
    Get the organization name from the request state (set by middleware).
    
    Parameters
    ----------
    request : Request
        The FastAPI request object.
        
    Returns
    -------
    str
        The organization name from request state.
        
    Raises
    ------
    JSONResponse
        If organization name is not found in request state.
    """
    organization_name = getattr(request.state, 'organization_name', None)
    if not organization_name:
        raise HTTPException(
            status_code=500,
            detail="Organization name not found in request state. API key validation may have failed."
        )
    return organization_name 