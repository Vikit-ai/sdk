import datetime
import os
import shutil
import tempfile

import pytest
from loguru import logger

from vikit.common.context_managers import WorkingFolderContext

TEST_MARK = "test_mark"


@pytest.fixture(scope="function")
def custom_temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Remove the temporary directory after the test.
    shutil.rmtree(temp_dir)


@pytest.mark.unit
def test_working_folder_context__custom_root(custom_temp_dir):
    initial_path = os.getcwd()

    with WorkingFolderContext(
        root=custom_temp_dir,
        insert_date=False,
        insert_minutes=False,
        mark=TEST_MARK,
        include_mark=True,
        insert_small_id=False,
    ):
        current_path = os.getcwd()
        expected_path = os.path.join(os.path.realpath(custom_temp_dir), TEST_MARK)
        assert current_path == expected_path, (
            f"Wrong working folder. Expected: {expected_path}, was: {current_path}"
        )

    # Exited the working folder context.
    current_path = os.getcwd()
    assert current_path == initial_path, (
        f"Working folder not restored. Expected: {initial_path}, was: {current_path}"
    )


@pytest.mark.unit
def test_get_delivery_folder_suffix_today_with_date_and_mark_no_smallid():
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    with WorkingFolderContext(
        insert_date=True,
        date_format="%Y-%m-%d",
        insert_minutes=False,
        mark=TEST_MARK,
        insert_small_id=False,
    ) as wf:
        tested_suffix = wf.get_delivery_folder_suffix()
        logger.debug(f"tested_suffix is {tested_suffix}")

        assert tested_suffix.startswith(today), (
            f"expected {tested_suffix} to start with {today}"
        )
        assert tested_suffix.endswith(f"{TEST_MARK}"), (
            f"expected {tested_suffix} to end with {TEST_MARK}"
        )


@pytest.mark.unit
def test_get_delivery_folder_suffix_today_small_id_nomark():
    with WorkingFolderContext(
        insert_date=True,
        date_format="%Y-%m-%d",
        insert_minutes=False,
        include_mark=False,
        insert_small_id=True,
    ) as wf:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        tested_suffix = wf.get_delivery_folder_suffix()
        logger.debug(f"tested_suffix is {tested_suffix}")

        assert tested_suffix.startswith(today), (
            f"expected {tested_suffix} to start with {today}"
        )
        assert tested_suffix.endswith(f"{wf.small_id}"), (
            f"expected {tested_suffix} to end with {wf.small_id}"
        )


@pytest.mark.unit
def test_get_delivery_folder_suffix_nodate_small_id_with_mark():
    with WorkingFolderContext(
        insert_date=False,
        insert_minutes=False,
        mark=TEST_MARK,
        include_mark=True,
        insert_small_id=True,
    ) as wf:
        tested_suffix = wf.get_delivery_folder_suffix()
        logger.debug(f"tested_suffix is {tested_suffix}")
        assert tested_suffix.startswith(f"{TEST_MARK}"), (
            f"expected {tested_suffix} to start with {TEST_MARK}"
        )
        assert tested_suffix.endswith(f"{wf.small_id}"), (
            f"expected {tested_suffix} to end with {wf.small_id}"
        )


@pytest.mark.unit
def test_get_delivery_folder_suffix_nodate_small_id_no_mark():
    with WorkingFolderContext(
        insert_date=False,
        include_mark=False,
        insert_minutes=False,
        insert_small_id=True,
    ) as wf:
        tested_suffix = wf.get_delivery_folder_suffix()
        logger.debug(f"tested_suffix is {tested_suffix}")

        assert tested_suffix.startswith(wf.small_id), (
            f"expected {tested_suffix} to start with {wf.small_id}"
        )
        assert tested_suffix.endswith(wf.small_id), (
            f"expected {tested_suffix} to end with {wf.small_id}"
        )


@pytest.mark.unit
def test_invalid_mark_raises_error():
    with pytest.raises(
        ValueError, match="If include_mark is set, mark must be set also."
    ):
        with WorkingFolderContext(include_mark=True, mark=None):
            pass
