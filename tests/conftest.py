def pytest_addoption(parser):
    parser.addoption(
        "--replace-gold",
        action="store_true",
        help="don't check gold output and instead overwrite it",
    )


def pytest_generate_tests(metafunc):
    if "replace_gold" in metafunc.fixturenames:
        if metafunc.config.getoption("replace_gold"):
            metafunc.parametrize("replace_gold", [True])
        else:
            metafunc.parametrize("replace_gold", [False])
