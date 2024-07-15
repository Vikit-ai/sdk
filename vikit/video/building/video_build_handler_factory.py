from vikit.video_building import VideoBuildHandler


class VideoBuildHandlerFactory:
    def __init__(self):
        self._handlers = {}

    def register_handler(self, handler: VideoBuildHandler):
        self._handlers[handler.get_name()] = handler

    def get_handler(self, name) -> VideoBuildHandler:
        return self._handlers[name]

    def get_handler_names(self) -> list[str]:
        return self._handlers.keys()

    def get_handler_list(self) -> list[VideoBuildHandler]:
        return self._handlers.values()
