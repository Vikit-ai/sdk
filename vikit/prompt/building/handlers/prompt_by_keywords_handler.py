from urllib.request import urlretrieve

from vikit.prompt.building.prompt_building_handler import PromptBuildingHandler
from vikit.video.video import Video
from vikit.video.video_build_settings import VideoBuildSettings


class PromptByKeywordsHandler(PromptBuildingHandler):
    def __init__(self):
        super().__init__()

    def supports_async(self):
        return True

    async def _execute_logic_async(
        self, prompt: str, build_settings: VideoBuildSettings, **kwargs
    ) -> str:
        super()._execute_logic_async(video)
        """
        Process the video generation binaries: we actually do ask the video to build itself
        as a video binary (typically an MP4 generated from Gen AI, hosted behind an API),
        or to compose from its inner videos in case of a child composite video

        Args:
            video (Video): The video to process
            build_settings (VideoBuildSettings): The build settings
            **kwargs: Additional arguments

        Returns:
            an enhanced prompt to be used for video generation
        """
        super()._execute_logic_async(prompt, **kwargs)
        if build_settings.generate_from_llm_keyword:
            # Get more colorfull keywords from prompt, and a title and handle excluded words
            enhanced_prompt, self._title = await build_settings.get_ml_models_gateway().get_keywords_from_prompt_async(
                    subtitleText=prompt, excluded_words=kwargs["enhanced_prompt"])
            self._keywords = enhanced_prompt
        else:
            # Get more colorfull prompt from current prompt text
            enhanced_prompt, enhanced_title = (
                await ml_gateway.get_enhanced_prompt_async(self._text)
            )
            if self._title is None:
                self._title = ft.get_safe_filename(enhanced_title)
            self._keywords = None

            
            
            
             enhanced_prompt =  await ( 
                build_settings.get_ml_models_gateway().get_keywords_from_prompt_async(
                    kwargs["enhanced_prompt"]
                )
            )
        )

        file_name = self.get_file_name_by_state(video.build_settings)
        video._media_url = urlretrieve(
            video_link_from_prompt,
            file_name,
        )[0]
        video.metadata.is_video_generated = True

        return video

    def _execute_logic(self, video: Video, **kwargs) -> Video:
        """
        Process the video generation  synchronously
        """
        super()._execute_logic(video)
        video_link_from_prompt = (  # Should give a link on a web storage
            video.build_settings.get_ml_models_gateway().generate_video_async(
                kwargs["enhanced_prompt"]
            )
        )

        file_name = self.get_file_name_by_state(video.build_settings)
        video._media_url = urlretrieve(
            video_link_from_prompt,
            file_name,
        )[0]
        video.metadata.is_video_generated = True

        return video
