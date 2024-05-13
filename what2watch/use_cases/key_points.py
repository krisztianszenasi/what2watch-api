from what2watch.models.key_point import KeyPoint
from what2watch.models.transcript import TranscriptChunk
from what2watch.use_cases.transcript import get_transcripts_as_langchain_documents
from what2watch.langchain_related.prompts.key_points import key_point_question_prompt, key_point_refine_prompt
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import TokenTextSplitter
from langchain_community.chat_models import ChatOpenAI
from typing import List
from difflib import SequenceMatcher, Match


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
            starting_words.strip(),
            transcripts=TranscriptChunk.query.filter_by(video_id=video_id).all(),
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
    starting_words: str,
    transcripts: List[TranscriptChunk]
) -> TranscriptChunk:
    previous_transcript: TranscriptChunk
    previous_match: Match = None
    for transcript in transcripts:
        current_match = SequenceMatcher(None, starting_words, transcript.text).find_longest_match()
        if complete_match_found(current_match, previous_match, starting_words):
            if complete_match_in(current_match, starting_words):
                return transcript
            elif match_splitted_at_word_break(current_match, previous_match, previous_transcript.text):
                return previous_transcript
        previous_match = current_match
        previous_transcript = transcript
    return None


def complete_match_found(match_a: Match, match_b: Match, words: str) -> bool:
    return get_len(match_a) + get_len(match_b) >= len(words) - 1


def complete_match_in(match_obj: Match, words: str) -> bool:
    return get_len(match_obj) == len(words)


def match_splitted_at_word_break(current: Match, previous: Match, words: str) -> bool:
    return match_starts_at_beginning(current) and match_stops_at_end(previous, words)


def match_starts_at_beginning(match_obj: Match) -> bool:
    try:
        return match_obj.b == 0
    except AttributeError:
        return False


def match_stops_at_end(match_obj: Match, words: str) -> bool:
    try:
        return match_obj.b + match_obj.size == len(words)
    except AttributeError:
        return False


def get_len(match_obj: Match) -> int:
    try:
        return match_obj.size
    except AttributeError:
        return 0