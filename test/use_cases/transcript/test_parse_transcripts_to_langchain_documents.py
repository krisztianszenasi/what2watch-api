from importlib import metadata
from unittest import TestCase

from what2watch.models.transcript import TranscriptChunk
from what2watch.use_cases.transcript import parse_transcripts_to_langchain_documents
from langchain_core.documents import Document


class ParseTranscriptToDocuments(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.video_id = 1
        cls.words = ['these', 'are', 'the', 'word']
        cls.transcripts = [
            TranscriptChunk(video_id=cls.video_id, text=word)
            for word in cls.words
        ]
        cls.expected = [Document(metadata={'video_id': cls.video_id}, page_content=' '.join(cls.words))]

    def test__when_empty_transcripts__returns_empty_list(self):
        result = parse_transcripts_to_langchain_documents([])

        self.assertEqual(result, [])

    def test__when_not_empty_transcripts__returns_list_of_documents(self):
        result = parse_transcripts_to_langchain_documents(self.transcripts)
        self.assertEqual(result, self.expected)