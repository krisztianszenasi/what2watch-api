from langchain.prompts import PromptTemplate


key_point_refine_prompt = PromptTemplate.from_template(
    """
    Each key point should look like this:
    <starts_from>: <key_point_text>
    Where <starts_from> is the first 4 words from where the key points starts from in the original text.
    Where <key_point_text> is the key point you made up from the text.

    Your job is to produce a final list of important key points.
    We have provided the existing key points up to a certain point: {existing_answer}
    We have the opportunity to add additional key points to the existing ones (only if needed)
    with given context below:
    ------------
    {text}
    ------------
    Given the new context, extend the key points list.
    If the context isn't useful, return the original key points list.
    """ 
)

key_point_question_prompt = PromptTemplate.from_template(
    """
    Each key point should look like this:
    <starts_from>: <key_point_text>
    Where <starts_from> is the first 4 words from where the key points starts from in the original text.
    Where <key_point_text> is the key point you made up from the text.

    Given the text below gather the important key points:
    
    "{text}"
    
    
    Key points:
    """
)