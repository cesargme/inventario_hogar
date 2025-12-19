import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session, select

from database.db import get_session
from database.models import User

security = HTTPBasic()


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    """Verifica las credenciales HTTP Basic Auth"""

    # Buscar usuario en DB
    statement = select(User).where(User.username == credentials.username)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Verificar password
    if not bcrypt.checkpw(
        credentials.password.encode(), user.password_hash.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user
