def pytest_addoption(parser):
    parser.addoption("--ignore-images", action="store_true", default=False)


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.ignore_images
    if "ignore_images" in metafunc.fixturenames:
        metafunc.parametrize("ignore_images", [option_value])
