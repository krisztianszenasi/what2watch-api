from unittest import TestCase

from what2watch.models.transcript import TranscriptChunk
from what2watch.use_cases.key_points import find_matching_transcript


class FindMatchingTranscriptTestCase(TestCase):

    def test_when_no_match_found_returns_none(self):
        starting_words = 'these are the starting words'
        transcripts = [TranscriptChunk(text='something different') for _ in range(10)]

        found = find_matching_transcript(starting_words, transcripts)

        self.assertEqual(found, None)

    def test_when_transcript_has_whole_text_only_returns_it(self):
        starting_words = 'these are the starting words'
        matching_transcript = TranscriptChunk(text=starting_words)
        un_matching_transcript = TranscriptChunk(text='something different')

        matching_only = [matching_transcript]
        un_matching_followed_by_matching = [un_matching_transcript, matching_transcript]

        self.assertEqual(
            find_matching_transcript(starting_words, matching_only),
            matching_transcript,
        )
        self.assertEqual(
            find_matching_transcript(starting_words, un_matching_followed_by_matching),
            matching_transcript,
        )

    def test_when_transcript_has_whole_text_with_additional_returns_it(self):
        starting_words = 'these are the starting words'
        matching_text = f'additional {starting_words} additional'
        matching_transcript = TranscriptChunk(text=matching_text)
        un_matching_transcript = TranscriptChunk(text='something different')

        matching_only = [matching_transcript]
        un_matching_followed_by_matching = [un_matching_transcript, matching_transcript]

        self.assertEqual(
            find_matching_transcript(starting_words, matching_only),
            matching_transcript,
        )
        self.assertEqual(
            find_matching_transcript(starting_words, un_matching_followed_by_matching),
            matching_transcript,
        )

    def test_when_starting_words_split_returns_first(self):
        starting_words = 'these are the starting words'
        break_point = len(starting_words) // 2
        splitted_first = TranscriptChunk(text=starting_words[0:break_point])
        splitted_second = TranscriptChunk(text=starting_words[break_point:])

        transcripts = [splitted_first, splitted_second]

        self.assertEqual(
            find_matching_transcript(starting_words, transcripts),
            splitted_first,
        )

    def test_when_starting_words_split_with_additional_returns_first(self):
        starting_words = 'these are the starting words'
        break_point = len(starting_words) // 2
        splitted_first = TranscriptChunk(text='additional' + starting_words[0:break_point])
        splitted_second = TranscriptChunk(text=starting_words[break_point:] + 'additional')

        transcripts = [splitted_first, splitted_second]

        self.assertEqual(
            find_matching_transcript(starting_words, transcripts),
            splitted_first,
        )

    def test_when_only_partial_match_returns_none(self):
        starting_words = 'these are the starting words'
        break_point = len(starting_words) // 2
        splitted_first = TranscriptChunk(text='additional' + starting_words[0:break_point])
        splitted_second = TranscriptChunk(text=starting_words[break_point:] + 'additional')

        transcripts = [splitted_second, splitted_first]

        self.assertEqual(
            find_matching_transcript(starting_words, transcripts),
            None,
        )