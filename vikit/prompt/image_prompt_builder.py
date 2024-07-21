import numpy as np

from vikit.common.decorators import log_function_params
from vikit.prompt.image_prompt import ImagePrompt


class ImagePromptBuilder:
    """
    Builds an image prompt

    Most functions are used by a prompt builder, as the way to generate a prompt may vary and get a bit complex
    """

    def __init__(self):
        super().__init__()
        self.prompt = ImagePrompt()

    @log_function_params
    def set_prompt_image(self, image: np.ndarray):
        if image is None:
            raise ValueError("The image prompt is not provided")
        self.prompt._image = image
        return self

    def build(self):
        return self.prompt
