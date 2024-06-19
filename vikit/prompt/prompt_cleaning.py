import re

from vikit.common.decorators import log_function_params


@log_function_params
def cleanse_llm_keywords(input):
    """
    cleanse a text usually provided by an LLM so that it can be consumed
    downstream for video generation

    Args:
        input: The text to cleanse

    Returns:
        The cleansed text

    """
    if input is None:
        raise AttributeError("The input text is None")

    # initialization of string to ""
    new_keywords = ""
    # s = input.split("\n")

    for x in input:
        if x:
            # traverse in the string

            # Remove numbers, dots, and newline characters using regex
            new_keywords += re.sub(r"[\d.]+", "", x)
            # Remove special characters
            new_keywords = re.sub(r"[^\w\s]", "", new_keywords)
            # Remove leading and trailing whitespaces
            new_keywords = new_keywords.lstrip()
            # remove backslashes
            new_keywords = new_keywords.replace("\\", "")
            # Replace multiple consecutive commas with a single comma
            new_keywords = re.sub(r",+", ",", new_keywords)
            # remove newlines
            new_keywords = new_keywords.replace("\n", "")
            # old filter, for the records:   new += "".join([i for i in x if not i.isdigit() and i != "."]) + ", "

    return new_keywords
