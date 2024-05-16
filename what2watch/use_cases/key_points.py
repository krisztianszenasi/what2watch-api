from what2watch.models.key_point import KeyPoint
from what2watch.models.transcript import TranscriptChunk
from what2watch.use_cases.transcript import get_transcripts_as_langchain_documents
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from typing import List, Dict, Optional
from difflib import SequenceMatcher, Match
from what2watch.langchain_related.prompts.key_points import key_points_prompt
from what2watch.langchain_related.parsers.key_points import response_parser


def generate_video_key_points(video_id: str) -> List[KeyPoint]:
    """Generate key points for a given video.
    
    For each key point a matching transcript is tried to be found via the 
    `find_matching_transcript_for` function. It uses the `starting_words`
    parameter provided by the llm. Sometimes these words cannot be matched to
    any existing transcript. In that case the function falls back to the
    previous transcript.

    Args:
        video_id (str): Video to generate for.

    Returns:
        List[KeyPoint]: Key points generated.
    """
    key_points_response: List[Dict] = get_key_points_prompt_response(video_id)
    key_points: List[KeyPoint] = []

    previous_transcript_chunk: TranscriptChunk = None
    for key_point in key_points_response:
        starting_words = key_point.get('starting_words')
        text = key_point.get('text')

        matching_transcript = find_matching_transcript_for(
            starting_words=starting_words,
            video_id=video_id,
            start_searching_from=previous_transcript_chunk,
        )

        key_points.append(KeyPoint(
            video_id=video_id,
            text=text,
            starts_from=matching_transcript or previous_transcript_chunk,
            starting_words=starting_words,
        ))
        previous_transcript_chunk = matching_transcript or previous_transcript_chunk
    return key_points



def get_key_points_prompt_response(video_id: str) -> List[Dict]:
    """Generate key points via a specified llm model."""
    transcript = get_transcripts_as_langchain_documents(video_id)
    splitter = RecursiveCharacterTextSplitter(chunk_size=8500, chunk_overlap=0)
    chunks = splitter.split_documents(transcript)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    chain = key_points_prompt | llm | response_parser

    key_points: List[Dict] = []
    for chunk in chunks:
        current_response: Dict = chain.invoke(chunk)
        key_points.extend(current_response.get('key_points', []))
    return key_points


def find_matching_transcript_for(
        starting_words:
        str, video_id: str,
        start_searching_from: Optional[TranscriptChunk] = None,
    ) -> TranscriptChunk:
    """Wrapper function for `find_matching_transcript`.

    It simply filters the `TranscriptChunk` models with the given `video_id`.
    The parameter `start_searching_from` is used for speeding up the search.
    """
    transcript_query = TranscriptChunk.query.filter_by(video_id=video_id)
    if start_searching_from is not None:
        transcript_query = transcript_query.filter(TranscriptChunk._id > start_searching_from._id)

    return find_matching_transcript(
        starting_words=starting_words,
        transcripts=transcript_query,
    )


def find_matching_transcript(
    starting_words: str,
    transcripts: List[TranscriptChunk],
) -> TranscriptChunk:
    """Finds the transcript object that contains the starting words.
    
    For each iteration it checks whether the `starting_words` were found in
    either the previous or current transcript.

    If it was found there are two possible scenarios:
        - The `starting_words` are in the current transcript completely.
        - The `starting_words` are splitted between two transcripts.

    In the latter case two additional conditions must be checked:
        - The `starting_words` are in the end of the previous transcript
        - The `starting_words` are int the beginning of the current transcript. 
    """
    previous_transcript: TranscriptChunk = None
    previous_match: Match = None
    for current_transcript in transcripts:
        current_match = SequenceMatcher(None, starting_words.lower(), current_transcript.text.lower()).find_longest_match()
        if complete_match_found(current_match, previous_match, starting_words):
            if complete_match_in(current_match, starting_words):
                return current_transcript
            elif match_splitted_at_word_break(current_match, previous_match, previous_transcript):
                return previous_transcript
        previous_match = current_match
        previous_transcript = current_transcript
    return None


def complete_match_found(match_a: Match, match_b: Match, words: str) -> bool:
    """Check whether a complete match is found.

    If the `words` are split between the transcripts a space character is lost.
    Thats the reason for the >= comparison and the -1 at the end.
    """
    return get_len(match_a) + get_len(match_b) >= len(words) - 1


def complete_match_in(match_obj: Match, words: str) -> bool:
    return get_len(match_obj) == len(words)


def match_splitted_at_word_break(current: Match, previous: Match, transcript: Optional[TranscriptChunk]) -> bool:
    if transcript is None:
        return False
    return match_starts_at_beginning(current) and match_stops_at_end(previous, transcript.text)


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