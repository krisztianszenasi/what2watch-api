from flask import Blueprint, request, jsonify

from what2watch.extensions import db
from what2watch.models.video import Video
from what2watch.use_cases.transcript import (
    retrieve_and_save_transcripts_to_db, retrieve_paginated_transcript_chunks,
    transcripts_exist_in_db_for)
from what2watch.use_cases.video import generate_video_summary, get_video_from_db_or_api_and_save_or_404, video_is_valid_or_400
from what2watch.use_cases.key_points import generate_video_key_points

video = Blueprint('video', __name__)


@video.errorhandler(400)
def bad_request(error):
    """Custom bad request response."""
    return jsonify({'error': 'Bad Request', 'message': error.description}), 400

@video.errorhandler(404)
def not_found(error):
    """Custom not found response."""
    return jsonify({'error': 'Not Found', 'message': error.description}), 404


@video.route('/video/<video_id>')
def get_video(video_id: str):
    """Displays some basic information about a youtube video.

    404 error when the video does not exist.
    """
    video: Video = get_video_from_db_or_api_and_save_or_404(video_id)
    return {'result': video.as_dict()}


@video.route('/video/<video_id>/transcript_chunks')
def get_transcript_chunks(video_id: str):
    """Displays a paginated response for available transcript chunks.

    Currently only english transcription is supported.
    If it does not exists returns 400 bad request.

    Available query parameters:
        page (int): Page index. Defaults to 1.
        size(int): Page size. Default to 50.
    """
    video: Video = get_video_from_db_or_api_and_save_or_404(video_id)

    if not transcripts_exist_in_db_for(video_id):
        retrieve_and_save_transcripts_to_db(video)

    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('size', 50))

    return {
        'results': [
            transcript.as_dict()
            for transcript in retrieve_paginated_transcript_chunks(video_id, page, page_size)
        ]
    }


@video.route('/video/<video_id>/summary')
def get_summary(video_id: str):
    """Displays a summary generated via an llm from the video's transcript.
    
    If the video is longer than the specified max length the endpoint returns
    400 bad request.

    It can be modified via an environmental variable `VIDEO_LENGTH_LIMIT` and
    it defaults to 15 minutes. If you would like no limits set it to -1.
    """
    video: Video = get_video_from_db_or_api_and_save_or_404(video_id)
    video_is_valid_or_400(video)
    if not transcripts_exist_in_db_for(video_id):
        retrieve_and_save_transcripts_to_db(video)
    if video.summary is None:
        video.summary = generate_video_summary(video_id)
        db.session.commit()
    return {'result': video.summary}


@video.route('/video/<video_id>/key-points')
def get_key_points(video_id: str):
    """Displays a key points generated via an llm from the video's transcript.
    
    Same rules are applied here like at the `get_summary` endpoint.
    """
    video: Video = get_video_from_db_or_api_and_save_or_404(video_id)
    video_is_valid_or_400(video)
    if not transcripts_exist_in_db_for(video_id):
        retrieve_and_save_transcripts_to_db(video)

    if not video.key_points:
        video.key_points.extend(generate_video_key_points(video_id))
        db.session.commit()
    return {
        'results': [
            key_point.as_dict()
            for key_point in video.key_points
        ]
    }
