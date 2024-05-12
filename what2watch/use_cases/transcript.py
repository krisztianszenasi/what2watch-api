from what2watch.extensions import db
from what2watch.models import TranscriptChunk, Video
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_core.documents import Document
from flask import abort


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


def retrieve_paginated_transcript_chunks(video_id: str, page: int, page_size: int) -> list[TranscriptChunk]:
    return TranscriptChunk.query.filter_by(video_id=video_id).paginate(page=page, per_page=page_size)


def get_transcripts_as_langchain_documents(video_id: str) -> list[Document]:
    document = Document(metadata={'video_id': video_id}, page_content='')
    for transcript_chunk in TranscriptChunk.query.filter_by(video_id=video_id).all():
        document.page_content += transcript_chunk.text
    return [document]