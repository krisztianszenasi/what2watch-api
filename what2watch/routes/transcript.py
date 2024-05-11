from flask import Blueprint, request

from what2watch.extensions import db
from what2watch.models.video import Video
from what2watch.use_cases.transcript import (
    retrieve_and_save_transcripts_to_db, retrieve_paginated_transcript_chunks,
    transcripts_exist_in_db_for)
from what2watch.use_cases.video import (
    generate_video_summary, get_video_from_db_or_api_and_save_or_404)

transcript = Blueprint('transcript', __name__)


@transcript.route('/video/<video_id>')
def get_video(video_id: str):
    video: Video = get_video_from_db_or_api_and_save_or_404(video_id)
    return {'result': video.as_dict()}


@transcript.route('/video/<video_id>/transcript_chunks')
def get_transcript_chunks(video_id: str):
    video: Video = get_video_from_db_or_api_and_save_or_404(video_id)
    if not transcripts_exist_in_db_for(video_id):
        retrieve_and_save_transcripts_to_db(video)
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('size', 50))

    results = [
        transcript.as_dict()
        for transcript in retrieve_paginated_transcript_chunks(video_id, page, page_size)
    ]

    return {
        'results': results
    }


@transcript.route('/video/<video_id>/summary')
def get_summary(video_id: str):
    video = Video.query.get_or_404(video_id)
    if not transcripts_exist_in_db_for(video_id):
        retrieve_and_save_transcripts_to_db(video)
    # if video.summary is None:
    summary = generate_video_summary(video_id)
    video.summary = summary
    db.session.commit()
    return {'result': video.summary}

