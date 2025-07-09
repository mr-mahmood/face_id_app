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


def validate_gate_and_roll(gate: str, roll: str):
    """
    Validate the gate and roll values for camera-related endpoints.

    Parameters
    ----------
    gate : str
        The gate name to validate (should be at least 3 characters).
    roll : str
        The camera role to validate (should be either 'entry' or 'exit').

    Returns
    -------
    tuple
        (is_valid, error_message):
            is_valid : bool
                True if both gate and roll are valid, False otherwise.
            error_message : str
                Error message if validation fails, empty string if valid.
    """
    gate = gate.lower()
    roll = roll.lower()
    if len(gate) <= 3:
        return False, "Gate name must be at least 4 characters."
    if roll not in ["entry", "exit"]:
        return False, "Roll must be either 'entry' or 'exit'."
    return True, "" 