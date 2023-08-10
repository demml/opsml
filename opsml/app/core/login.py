# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


username = os.environ["OPSML_USERNAME"].encode("utf-8")
password = os.environ["OPSML_PASSWORD"].encode("utf-8")


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    is_correct_username = secrets.compare_digest(current_username_bytes, username)
    current_password_bytes = credentials.password.encode("utf8")
    is_correct_password = secrets.compare_digest(current_password_bytes, password)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
