# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

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
            # remove quotes
            new_keywords = new_keywords.replace("'", " ")
            # remove double quotes
            new_keywords = new_keywords.replace("\"", " ")
            # Replace multiple consecutive commas with a single comma
            new_keywords = re.sub(r",+", ",", new_keywords)
            # remove newlines
            new_keywords = new_keywords.replace("\n", "")
            # old filter, for the records:   new += "".join([i for i in x if not i.isdigit() and i != "."]) + ", "

    return new_keywords
