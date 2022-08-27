import pytest
from mkreports.md import IDStore


@pytest.fixture
def page_fixtures(tmp_path):
    return dict(
        store_path=tmp_path,
        report_path=tmp_path,
        javascript_path=tmp_path,
        project_root=tmp_path,
        page_path=tmp_path,
        idstore=IDStore(),
    )


def pytest_addoption(parser):
    parser.addoption("--ignore-images", action="store_true", default=False)


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.ignore_images
    if "ignore_images" in metafunc.fixturenames:
        metafunc.parametrize("ignore_images", [option_value])
