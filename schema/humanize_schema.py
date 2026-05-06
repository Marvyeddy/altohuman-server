from pydantic import BaseModel

class AiHumanizer(BaseModel):
    text: str
    action: str