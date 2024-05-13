from what2watch.extensions import db
from what2watch.models import Video
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError
from flask import abort
from langchain.text_splitter import TokenTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from what2watch.langchain_related.prompts.video_summary import question_prompt, refine_prompt
from what2watch.use_cases.transcript import get_transcripts_as_langchain_documents


VIDEO_LENGTH_LIMIT = 15 * 60

def video_is_valid_or_400(video: Video):
    if video_is_too_long(video):
        abort(400, description='Video is too long!\nwhat2watch works best with videos under 15 minutes longs.')

def video_is_too_long(video: Video) -> bool:
    return video.length > VIDEO_LENGTH_LIMIT


def get_video_from_db_or_api_and_save_or_404(video_id: str) -> Video:
    if not video_exists_in_db(video_id):
        retrieve_video_from_api_and_save_to_db(video_id)
    return Video.query.get_or_404(video_id)


def video_exists_in_db(video_id: str) -> bool:
    return Video.query.get(video_id) is not None


def retrieve_video_from_api_and_save_to_db(video_id: str) -> Video:
    if video := retrieve_video_from_api(video_id):
        db.session.add(video)
        db.session.commit()
        return video
    return None


def retrieve_video_from_api(video_id: str) -> Video | None:
    try:
        pytube_result = YouTube.from_id(video_id)
        return Video(
            _id=video_id,
            title=pytube_result.title,
            description=pytube_result.description,
            view_count=pytube_result.views,
            thumbnail_url=pytube_result.thumbnail_url,
            publish_date=pytube_result.publish_date,
            length=pytube_result.length,
            author=pytube_result.author,
        )
    except (VideoUnavailable, RegexMatchError):
        return None
    

def generate_video_summary(video_id: str) -> str:
    transcript = get_transcripts_as_langchain_documents(video_id)
    splitter = TokenTextSplitter(model_name='gpt-3.5-turbo', chunk_size=10000, chunk_overlap=100)
    chunks = splitter.split_documents(transcript)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    summarize_chain = load_summarize_chain(
        llm=llm,
        chain_type='refine',
        question_prompt=question_prompt,
        refine_prompt=refine_prompt,
        document_variable_name='text', 
        initial_response_name='existing_answer'
    )
    return summarize_chain.run(chunks)
