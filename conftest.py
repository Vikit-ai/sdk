# conftest.py
import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


# Fixture to track the currently running test
@pytest.fixture(autouse=True)
def log_test_start_and_finish(request):
    logger.info(f"Starting test: {request.node.name}")
    yield
    logger.info(f"Finished test: {request.node.name}")


# Hook to log the start of each test
def pytest_runtest_logstart(nodeid, location):
    logger.info(f"Test started: {nodeid}")


# Hook to log the finish of each test
def pytest_runtest_logfinish(nodeid, location):
    logger.info(f"Test finished: {nodeid}")
