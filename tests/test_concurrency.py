from concurrent.futures import ProcessPoolExecutor
from queue import PriorityQueue
import time
import os

import unittest
import warnings

from vikit.video import prompt_based_video, video_build_settings
import tests.tests_tools as tools
from vikit.common.context_managers import WorkingFolderContext


class TestConcurrency(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @unittest.skip("Test skipped before resolution")
    def test_generate_video_tree(self):
        """
        Test that the video tree is correctly generated when using a priority queue and
        a process executor.
        """
        with WorkingFolderContext() as working_folder:
            build_settings = video_build_settings.VideoBuildSettings(
                run_async=False, test_mode=True
            )
            test_prompt = tools.test_prompt_library["tired"]
            prompt_vid = prompt_based_video.PromptBasedVideo(test_prompt)

            built_vid = prompt_vid.build(build_settings=build_settings)

            assert built_vid is not None
            assert built_vid.media_url is not None

            files = [
                f
                for f in os.listdir(working_folder.path)
                if os.path.isfile(os.path.join(working_folder.path, f))
            ]

            "keywords_from_prompt_file_transition_keywords_from_prompt_file_to_A-abandoned_A-abandoned"

            print("Fichiers dans '", working_folder.path, "':")
            for file in files:
                # so we expect to see the following:
                # - the generated (or fake) video files
                # - the subtitle files
                # - the background music file
                # - the prompt audio file
                # - the transition files
                # - the first and last frame images for transitions
                # - the composite video files: one global with expected name and one for each subtitle

                self.assert_exists_generated_video(
                    files, len(test_prompt.subtitles) * 2
                )  # 2 generated videos per subtitle
                self.assert_exists_transitions(
                    files, len(test_prompt.subtitles)
                )  # one transition per subtitle
                self.assert_exists_composite_videos(
                    files, len(test_prompt.subtitles) + 1
                )  # one composite per subtitle +1 for the global video
                self.assert_exists_subtitle(files, 0)
                self.assert_exists_generated_audio_prompt(files, 0)
                self.assert_exists_generated_bg_music(files, 0)
                self.assert_exists_default_bg_music(files, 0)

                print(file)


#     def test_concurrent_tasks(self):
#         with ProcessPoolExecutor() as executor:
#             futures = []
#             while not tasks.empty():
#                 priority, task_name = tasks.get()
#                 future = executor.submit(task, task_name)
#                 futures.append(future)

#             # Attendre que toutes les tâches soient terminées
#             for future in futures:
#                 print(future.result())


# def task(name):
#     print(f"Exécution de la tâche {name}")
#     time.sleep(5)
#     return f"Tâche {name} terminée"


# # Créer une PriorityQueue pour gérer les tâches avec priorités
# tasks = PriorityQueue()
# tasks.put((2, "Tâche 1"))
# tasks.put((1, "Tâche 2"))
# tasks.put((3, "Tâche 3"))
