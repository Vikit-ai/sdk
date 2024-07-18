class MusicBuildingContext:
    def __init__(
        self,
        apply_background_music: bool = False,  # will apply background music to the prompt, generate_background_music won't be considered if apply_background_music False
        generate_background_music: bool = False,  # will generate music taking inspiration from the prompt
        use_recorded_prompt_as_audio: bool = False,
        expected_music_length: float = None,
    ):  # length in seconds, setting default to 0:

        self.use_recorded_prompt_as_audio = use_recorded_prompt_as_audio
        self.apply_background_music = apply_background_music
        self.generate_background_music = generate_background_music
        self.expected_music_length = expected_music_length
        self._generated_background_music_file = None
