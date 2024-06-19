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
        run_async: bool = True,
        test_mode: bool = False,
    ):
        self.delete_interim_files = delete_interim_files  # Not deleting the intermediate video files, first and last frames TODO: to be implemented
        # and any other resources is useful for debugging purposes and to reuse the data for further
        # video combinations, model trainings
        self.run_async = (
            run_async  # Run the video generation in async mode, to boost reactivity and
        )
        # performance of the application. Can be set to off for debugging purposes
        self.test_mode = test_mode  # Run the video generation in local mode, to run local and fast tests
        self._ml_models_gateway = None

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
