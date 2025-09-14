
from fastapi import APIRouter
import jwt, time, os

router = APIRouter()
SECRET = os.getenv("JWT_SECRET", "dev-secret")

@router.get("/demo-token")
def demo_token(role: str = "underwriter", sub: str = None):
    payload = {"sub": sub or (role + "-demo"), "roles": [role], "iat": int(time.time())}
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return {"token": token}
