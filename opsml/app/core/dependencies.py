from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


def verify_token(X_Authentication: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
