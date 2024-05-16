from langchain.prompts import PromptTemplate
from what2watch.langchain_related.parsers.key_points import response_parser


template = """\
You will be given a text. Your job is to collect the important key points from
this text.
{format_instructions}
{text}
"""


key_points_prompt = PromptTemplate(
    template=template,
    input_variables=['text'],
    partial_variables={'format_instructions': response_parser.get_format_instructions()},
)