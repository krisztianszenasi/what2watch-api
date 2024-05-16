from importlib import metadata
from what2watch.extensions import db
from what2watch.models import TranscriptChunk, Video
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_core.documents import Document
from flask import abort
from typing import List


def transcripts_exist_in_db_for(video_id: str) -> bool:
    return TranscriptChunk.query.filter_by(video_id=video_id).first() is not None


def retrieve_and_save_transcripts_to_db(video: Video):
    try:
        transcript_chunks = YouTubeTranscriptApi.get_transcript(video._id)
    except TranscriptsDisabled:
        abort(400, description='Subtitles are disabled for this video.')

    chunks = [
        TranscriptChunk(**{'video_id': video._id, **chunk_data})
        for chunk_data in transcript_chunks
    ]

    db.session.bulk_save_objects(chunks)
    db.session.commit()


def retrieve_paginated_transcript_chunks(video_id: str, page: int, page_size: int) -> List[TranscriptChunk]:
    return TranscriptChunk.query.filter_by(video_id=video_id).paginate(page=page, per_page=page_size)


def get_transcripts_as_langchain_documents(video_id: str) -> list[Document]:
    return parse_transcripts_to_langchain_documents(TranscriptChunk.query.filter_by(video_id=video_id))


def parse_transcripts_to_langchain_documents(transcripts: List[TranscriptChunk]) -> List[Document]:
    page_content=' '.join([transcript.text for transcript in transcripts])
    if page_content != '':
        return [Document(metadata=get_metadata_from(transcripts), page_content=page_content)]
    return []

    
def get_metadata_from(transcripts: List[TranscriptChunk]) -> dict:
    try:
        video_id = transcripts[0].video_id
    except (IndexError, AttributeError):
        video_id = None
    return {'video_id': video_id}