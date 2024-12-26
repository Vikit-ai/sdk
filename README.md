<div align="center">
<img src='./medias/vikit_logo.jpg' style="height:150px"></img>

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1SltMsYv4ExYJLSagLKsZqazmCludo8vC)

</div>

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

# Vikit.ai Software Development  Kit

[Vikit.ai](https://vikit.ai/)  SDK let you develop easily video generators leveraging generative AI and other AI models. You may see this as a langchain to orchestrate AI models and video editing tools. 
To see the video in full resolution, click on the GIF.
<!-- [![](https://img.youtube.com/vi/_ipNgOOcX5U/sddefault.jpg)](https://youtu.be/_ipNgOOcX5U)</div> -->
<a href='https://youtu.be/_ipNgOOcX5U'><img src='medias/gif1_Plato.gif'></a> <a href='https://youtu.be/_ipNgOOcX5U'><img src='medias/gif3_Plato.gif'></a>

<a href='https://youtu.be/Hd-r3Hy9XFs?si=PRAZqDueaCFEUK9n'><img src='medias/gif2_Paris_h.gif'></a>

## How to use Vikit.ai SDK?

You need a personal access token, which you can easily obtain from [here](https://www.vikit.ai/#/platform).  

- Vikit.ai SDK is easy to test standalone using [Google Colab](https://colab.research.google.com/drive/1SltMsYv4ExYJLSagLKsZqazmCludo8vC).

- It is easy to develop through Dev Containers. Dev container file and instructions are available [here](dev_containers.md)

### Requirements for local installation

- Python 3.8+ 
- `requirements.txt` contains requirements for python environment
- FFMPEG and FFPROBE (on mac, using homebrew: brew install ffmpeg and on linux, using apt-get: sudo apt-get install ffmpeg)
- ImageMagick (for subtitles only; on mac, using homebrew: brew install imagemagick and on linux, using apt-get: sudo apt-get install imagemagick) 



## Code examples

Generating a video from simple text prompt, with background music and voice over narration:

```python

import asyncio
from vikit.music_building_context import MusicBuildingContext
from vikit.prompt.prompt_factory import PromptFactory
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.video_build_settings import VideoBuildSettings

prompt = "Paris, the City of Light, is a global center of art, fashion, and culture, renowned for its iconic landmarks and romantic atmosphere. The Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral are just a few of the city's must-see attractions."

video_build_settings = VideoBuildSettings(
    music_building_context=MusicBuildingContext(
        apply_background_music=True,
        generate_background_music=True,
    ),
    include_read_aloud_prompt=True,
)

async def create_video():
    prompt = await PromptFactory().create_prompt_from_text(prompt_text)
    video = PromptBasedVideo(prompt=prompt)
    await video.build(build_settings=video_build_settings)

if __name__ == "__main__":
    asyncio.run(create_video())

```

You can orchestrate several videos, using ```CompositeVideo()```. Here is an example showing how to generate two videos from texts:

```python

import asyncio
from vikit.video.composite_video import CompositeVideo
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.video_build_settings import VideoBuildSettings


async def create_composite_video():
    prompt1 = "Paris, the City of Light, is a global center of art, fashion, and culture, renowned for its iconic landmarks and romantic atmosphere."
    prompt2 = "The Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral are just a few of the city's must-see attractions."

video1 = RawTextBasedVideo(prompt1)
video2 = RawTextBasedVideo(prompt2)

video_composite.append_video(video1).append_video(video2)

await video_composite.build(
    build_settings=VideoBuildSettings(
        output_video_file_name="Composite.mp4",
    )

    video_composite.append_video(video1).append_video(transit).append_video(video2)

    await video_composite.build(
        build_settings=VideoBuildSettings(
            output_video_file_name="Composite.mp4",
        )
    )

if __name__ == "__main__":
    asyncio.run(create_composite_video())

```

More elaborated examples can be found in [script_example.py](script_example.py) or in our [Google Colab](https://colab.research.google.com/drive/1yZ-GC0GxRP6zKZD2lJfi9Rz16nRezLaa#scrollTo=72LXhJCils2Q). For additional information, please refer to the [Documentation](https://vikitai.readthedocs.io/en/latest/).

## Support

If you've encountered a bug, have a feature request, or have any suggestions to improve the project, we encourage you to open an issue on our GitHub repository. To do so, go to the "Issues" tab in our GitHub repository and click "New Issue." Please provide a clear title and detailed description, including steps to reproduce, environment setup, and any relevant screenshots or code snippets. 
If you have questions, reach out to us **<hello@vikit.ai>**.

## Contribution guidelines

Wanna help? You're very welcome! 🚀 :

1. New PR: You submit your PR and explain clearly what you want to change. We will review your PR as soon as possible,
2. PR validation: If the PR passes all the quality checks then Vikit.ai team assign a reviewer,
3. PR review: If everything looks good, the reviewer(s) will approve the PR. Otherwise we will engage a discussion and iterate until completion,
4. CI tests & Merge: Once the PR is approved, which means all the CI tests passm someone from the vikit team merge the code to the main branch.

### How to contribute?

- Fork vikit repository into your own GitHub account.
- Create a new branch and make your changes to the code.
- Commit your changes and push the branch to your forked repository.
- Open a pull request on our repository.

### General guidelines and standards

Please make sure your changes are consistent with these common guidelines:

- Include unit tests when you contribute new features
- Keep API compatibility in mind when you change code
- Use messages as proposed here [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) when you commit your code, 
- Update the changelog: [Change Log best practices](https://keepachangelog.com/en/1.1.0/)
- We do use [Semantic Versioning](https://semver.org/) 
- Please identify yourself with a valid email address as explained here: [Setting your commit email address](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)

## Disclaimer

- The content generated by the models in this repository is the sole responsibility of the user who initiates the generation. Users must ensure that their use of the generated content complies with all applicable laws, regulations, and ethical guidelines. The project contributors are not liable for any misuse, harm, or legal implications resulting from the use of the models provided. Users are encouraged to exercise caution and discretion when using generative AI tools.
- If you use the default background music, which is royalty free, you still must comply with Pixabay Content License Agreement (https://pixabay.com/fr/service/license-summary/).
- Too many parallel video generation processes might slow things down, just keep an eye on your local CPU usage. Happy coding! 🚀😊
