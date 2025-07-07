from fastapi import Header


def get_api_key(x_api_key: str = Header(..., description="API key for authentication")):
    """
    Dependency to extract API key from header.
    
    This dependency is used to document the API key requirement in FastAPI docs.
    The actual validation is handled by middleware, but this ensures the header
    appears in the Swagger UI documentation.
    
    Parameters
    ----------
    x_api_key : str
        API key from X-API-Key header
        
    Returns
    -------
    str
        The API key value
        
    Notes
    -----
    - This dependency is for documentation purposes only
    - Actual validation is performed by middleware
    - The header will appear in FastAPI docs as required
    """
    return x_api_key 