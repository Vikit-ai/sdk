from vikit.common.config import (
    get_app_analytics_endpoint,
    use_app_analytics,
)
from vikit.common.secrets import get_app_analytics_api_key


from posthog import Posthog

posthog = Posthog(
    project_api_key=get_app_analytics_api_key(),
    host=get_app_analytics_endpoint(),
)


def capture_event(id, event):
    if use_app_analytics:
        posthog.capture(distinct_id=id, event=event)
