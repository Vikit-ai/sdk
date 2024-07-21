import numpy as np
from vikit.prompt.prompt import Prompt


class ImagePrompt(Prompt):
    """
    A class to represent an image prompt
    """

    def __init__(self, prompt_image: np.ndarray = None):
        super().__init__()
        # for the moment, it stays pure image prompte,
        # To Do: image + text prompting
        self._image = prompt_image
