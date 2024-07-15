import datetime
from random import randint

import vikit.gateways.ML_models_gateway_factory as mlfactory


class GeneralBuildSettings:
    """
    General build settings for the video generation

    The settings are:
    - delete_interim_files: whether to delete the intermediate video files, first and last frames
    - run_async: whether to run the video generation in async mode, to boost reactivity and performance of the application
    - test_mode: whether to run the video generation in local mode, to run local and fast tests
    """

    def __init__(
        self,
        delete_interim_files: bool = False,  # not implemented yet :)
        run_async: bool = False,
        test_mode: bool = False,
        use_multiprocessing: bool = False,
        output_path: str = None,  # The path where the video will be saved, could be local or remote (i.e. a cloud bucket or a streaming service)
    ):
        self.delete_interim_files = delete_interim_files  # Not deleting the intermediate video files, first and last frames TODO: to be implemented
        # and any other resources is useful for debugging purposes and to reuse the data for further
        # video combinations, model trainings
        self.run_async = (
            run_async  # Run the video generation in async mode, to boost reactivity and
        )
        self.use_multiprocessing = use_multiprocessing
        # performance of the application. Can be set to off for debugging purposes
        self.test_mode = test_mode  # Run the video generation in local mode, to run local and fast tests
        self._ml_models_gateway = None
        self._id = str(randint(1, 9999999999)).zfill(10)
        self._build_date = datetime.date.today().strftime("%Y-%m-%d")
        self._build_time = datetime.datetime.now().time().strftime("%H:%M")
        self._output_path = output_path if output_path else "."

    def get_ml_models_gateway(self):
        """
        Handy function to get the ML models gateway from the buildsettings, as it is used in many places
        like a context
        """
        if self._ml_models_gateway is None:
            self._ml_models_gateway = (
                mlfactory.MLModelsGatewayFactory().get_ml_models_gateway(
                    test_mode=self.test_mode
                )
            )
        return self._ml_models_gateway

    @property
    def id(self) -> str:
        """
        Get the id of the build settings
        """
        return self._id

    @property
    def build_date(self) -> str:
        """
        Get the build date, generated at the creation of the object
        """
        return self._build_date

    @property
    def build_time(self) -> str:
        """
        Get the build time, generated at the creation of the object
        """
        return self._build_time

    @property
    def output_path(self) -> str:
        """
        Get the output path where the video will be saved
        """
        return self._output_path

    @output_path.setter
    def output_path(self, output_path: str):
        """
        Set the output path where the video will be saved
        """
        self._output_path = output_path

        return self
