from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from langchain_core.output_parsers import JsonOutputParser


class KeyPointResponseModel(BaseModel):

    starting_words: str = Field(
        description='The first couple of words from where the key point starts in the original text without apostrophes. If you are not sure set to null.'
    )
    text: str = Field(description='an important key point generated from the text')


class KeyPointListResponseModel(BaseModel):

    key_points: List[KeyPointResponseModel]


response_parser = JsonOutputParser(pydantic_object=KeyPointListResponseModel)
