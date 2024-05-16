"""Key point related output parsers and models."""

from typing import List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


class KeyPointResponseModel(BaseModel):
    """Key point format that the llm model should strive for in it's responses.
    
    The field `staring_words` is used for looking up looking up
    `TranscriptChunk` models for exact timestamps.
    """

    starting_words: str = Field(
        description='The first couple of words from where the key point starts in the original text without apostrophes.'
    )
    text: str = Field(description='an important key point generated from the text')


class KeyPointListResponseModel(BaseModel):
    """Simple wrapper for `KeyPointResponseModel`s.

    The response will contain multiple key points.
    """

    key_points: List[KeyPointResponseModel]


response_parser = JsonOutputParser(pydantic_object=KeyPointListResponseModel)
