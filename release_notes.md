<div align="center">
<a href="http://vikit.ai">
  <img src="./medias/vikit_logo.jpg" alt="Vikit Logo" style="height:150px">
</a>



</div>

# Vikit.ai Software Development  Kit - Release notes


## under development :  better prompts, simpler to build, models negative prompts, SDK easier to use and install

- Better prompts: we are working on a enriched prompt generation model that will allow for more coherent and engaging video scripts. This follows the work done during sessions with Microsoft AI Co-innovation lab in SF to better leverage Chatgpt 4o.

- Simpler to build: we are working on simplifying the prompts features and the way to build them, so you can add many more descriptions of your scenes and let the AI do the rest (depending on target model capabilities)

- Models negative prompts: integration of negative prompts to avoid certain elements in the scene 

- PIP package and Dev Container version: we are working on a PIP package to make it easier to install and use the SDK. We are also working on a Dev Container version to make it easier to develop with the SDK.

## V0.2 : Faster, more providers and Image Prompts

Now you have the possibility to use Image Based Prompt, kinda cool! 😎 Why doing this? You may want to start your new scenes from previous scenes context (for instance leverage ```get_last_frame_as_image```), or guide the video generation models with a given aesthetic.

Vikit 0.2 now implements async (at last 😉) and it is combined with multi processing support, which means video should take an average of 5 to 7 minutes to be fully generated, whatever the size of the prompts, depending on your own hardware, i.e. network bandwidth and CPU for ffmpeg video editing.
Async allows for gathering the different video scenes without blocking the main video building workflow, as if it where all done in parallel.
Multiprocessing is used to leverage all your computer cores when editing the video with all those generated or imported videos, as well as background music, read aloud prompt, or re-encoding.
Note: a Dev Environment version is in the works to get you started quickly with a full fledged dev environment, so you may benefit from Github x core VM's if needed. Also we received feedback that code is cool though a PIP version would be nice too for direct use.

Last but not least, we now integrate with **Stability AI** (for testing purpose) and **Haiper**, and still have the possibility to use **VideoCrafter**! The first two providers let you leap forward in the quality of generated video, enjoy!
Important note: Haiper do work, though we are working with their teams to figure out an operational issue , be sure we do everything for this feature to be back soon 🙂

Stay tuned for new integrations to come on the Video generation and music generation space ([Now what!](#and-now-what)).

Some other features you might want to experiment: 

- Prepare a video (```prepare_build```) with specific build settings, which means choosing your video generation provider, music, prompt, etc...all that can be applied with VideoBuildSettings object

- Also, the video generation process is streamlined trough two ways:

  1) You can now use Hooks to get your code run adjust before the build (```run_pre_build_actions_hook```) , during (```run_build_core_logic_hook```) and after build (run_post_build_actions_hook). Not too hard, huh?

  2) Handlers! just stack handlers in the order you want and let the process happen! You shall adapt or implement ```get_core_handlers``` function in the different type of ```Videos``` available to date set your own handlers if needs be...

Two additional features we hope you will find handy:

1) It is now possible to specify a target path where to save your videos. It could be a remote path provided you access it without authentication. Feel free to submit pull requests if you strongly need support for Cloud buckets or other target file systems.

2) You may cascade build settings, which means all the tree made of your composite video will share the same overall settings
## V0.1
This is the very first version, experimental MVP, of Vikit.ai SDK. 

It is private source and allows generating videos from an audio recording (e.g. a blog audio) or text. It also allows for merging the final video with background music and read aloud the prompt generated from text. 

Music can be generated, or a default royalty free background music. You may also use your own prompt recording as an audio track.

0.1 uses various models for video generation, music generation, audio prompt to text and synthetic voice generation.

Available type ov videos are:

- RawTextBasedVideo: the most basic building block that usually corresponds to a 2 to 6s video , depending on the generative model and platform providing it
- CompositeVideo: A video made of other video. You will probably play a lot with this beast and the RawTextBasedVideo!
- PromptBasedVideo: for lazy people like us 😉 who just want to give a prompt and let the video be generated. it inherits composite video and includes a first simple way to stich video and transitions together
- Imported (i.e. your video, generated or not)

You may with to experiment with 0.1 using this [Colab](https://colab.research.google.com/drive/1pb-dTGx3u98Vduy3FxrMi-cfESCZOcqG#scrollTo=72LXhJCils2Q), though video may take a long time to generate if you stack many scenes within (tens of minutes).

# And now what?
We will prioritize items according to community feedback. 

We are an open community, so you are more than welcomed to help improve Vikit to suit your needs! 
If you find the SDK useful please add GitHub stars ⭐️, and don't forget you can follow us on [LinkedIn](https://www.linkedin.com/company/vikit) , [YouTube](https://www.youtube.com/@vikitai) and [Discord](https://discord.com/invite/m5HpbpSnUT) !

Thanks for reading and supporting us! 