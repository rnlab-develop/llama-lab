from pydantic import BaseModel

# Pydantic models
class SearchRequest(BaseModel):
    text: str

class Document(BaseModel):
    id: int
    name: str

class SearchResponse(BaseModel):
    documents: list[Document]