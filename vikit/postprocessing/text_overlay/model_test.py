import pytest

from tests.medias.references_for_tests import RANCHO_FONT
from vikit.postprocessing.text_overlay.model import TextOverlayLineStyle


@pytest.mark.unit
def test_line_style__font_path_found__succeeds():
    TextOverlayLineStyle(font_path=RANCHO_FONT, font_size_pt=20)
    # No error should be raised.


@pytest.mark.unit
def test_line_style__font_path_not_found__fails():
    with pytest.raises(FileNotFoundError, match="unknown-font.ttf"):
        TextOverlayLineStyle(font_path="unknown-font.ttf", font_size_pt=20)
