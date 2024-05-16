"""Video summary related prompts.

These prompts are modified variants of the default ones provided by `langchain`
for their `RefineDocumentsChain` chain.
"""

from langchain.prompts import PromptTemplate

refine_prompt = PromptTemplate.from_template(
    """
    Your job is to produce a final summary about a video.
    We have provided an existing summary up to a certain point: {existing_answer}
    We have the opportunity to refine the existing summary (only if needed) with 
    some more context below.
    ------------
    {text}
    ------------
    Given the new context, refine the original summary.
    If the context isn't useful, return the original summary.
    """ 
)

question_prompt = PromptTemplate.from_template(
    """
    Write a concise summary of the following text about a video:
    
    
    "{text}"
    
    
    CONCISE SUMMARY:
    """
)
