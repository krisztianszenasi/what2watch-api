from what2watch.models.key_point import KeyPoint
from what2watch.models.transcript import TranscriptChunk
from what2watch.use_cases.transcript import get_transcripts_as_langchain_documents
from what2watch.langchain_related.prompts.key_points import key_point_question_prompt, key_point_refine_prompt
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import TokenTextSplitter
from langchain_community.chat_models import ChatOpenAI
from typing import List
from difflib import SequenceMatcher


def generate_video_key_points(video_id: str) -> List[KeyPoint]:
    key_points_text: str = generate_video_key_points_text(video_id)
    key_points_lines: List[str] = key_points_text.split('\n')

    previous_transcript_chunk: TranscriptChunk = None
    key_points: List[KeyPoint] = []

    for line in key_points_lines:
        if line == '' or ':' not in line:
            continue

        starting_words, key_point_text = line.split(':')
        matching_transcript = find_matching_transcript(
            video_id,
            starting_words.strip(),
            search_after=previous_transcript_chunk
        )
        key_points.append(KeyPoint(
            video_id=video_id,
            text=key_point_text.strip(),
            starts_from=matching_transcript,
            starting_words=starting_words,
        ))
        previous_transcript_chunk = matching_transcript
    return key_points



def generate_video_key_points_text(video_id: str) -> str:
    transcript = get_transcripts_as_langchain_documents(video_id)
    splitter = TokenTextSplitter(model_name='gpt-3.5-turbo', chunk_size=100000, chunk_overlap=0)
    chunks = splitter.split_documents(transcript)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    summarize_chain = load_summarize_chain(
        llm=llm,
        chain_type='refine',
        question_prompt=key_point_question_prompt,
        refine_prompt=key_point_refine_prompt,
        document_variable_name='text', 
        initial_response_name='existing_answer'
    )
    return summarize_chain.run(chunks)


def find_matching_transcript(
    video_id: str,
    starting_words: str,
    search_after: TranscriptChunk,
) -> TranscriptChunk:
    query = TranscriptChunk.query.filter_by(video_id=video_id)
    if search_after is not None:
        query = query.filter(TranscriptChunk._id > search_after._id)
    transcript: TranscriptChunk
    previous_transcript: TranscriptChunk
    previous_match_len = 0
    for transcript in query:
        current_match = SequenceMatcher(None, starting_words, transcript.text).find_longest_match()
        if previous_match_len + current_match.size >= len(starting_words) - 1:
            if previous_match_len == 0:
                return transcript
            return previous_transcript
        previous_match_len = current_match.size
        previous_transcript = transcript
    return None