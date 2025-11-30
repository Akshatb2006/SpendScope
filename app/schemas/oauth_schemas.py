from pydantic import BaseModel

class OAuthAuthorizeRequest(BaseModel):
    provider_id: str
    redirect_uri: str

class OAuthAuthorizeResponse(BaseModel):
    auth_url: str
    state: str

class OAuthCallbackRequest(BaseModel):
    code: str
    state: str

class OAuthCallbackResponse(BaseModel):
    status: str
    account_id: Optional[int] = None
    message: str