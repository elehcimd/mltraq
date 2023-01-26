import logging
import re

import mltraq
from mltraq.utils.log import IgnoredChainedCallLogger, default_exception_handler, init_logging, timeit


def test_log_enabled(caplog, capfd):
    with caplog.at_level(logging.INFO):
        with mltraq.options.option_context({"log.stdout": True}):
            mltraq.create_session()
    assert caplog.records[0].name == "mltraq"
    assert re.compile("^MLTRAQ .* initialized$").match(caplog.records[0].msg)

    out, err = capfd.readouterr()

    assert re.compile(".*MLTRAQ .* initialized.*").match(out)
    assert err == ""


def test_log_disabled(caplog, capfd):
    with caplog.at_level(logging.INFO):
        with mltraq.options.option_context({"log.stdout": False}):
            mltraq.create_session()

    assert re.compile("^MLTRAQ .* initialized$").match(caplog.records[0].msg)

    out, err = capfd.readouterr()

    assert out == ""
    assert err == ""


def test_timed(caplog):
    with caplog.at_level(logging.INFO):
        with mltraq.options.option_context({"log.stdout": True}):
            init_logging()

            @timeit
            def fast():
                pass

            fast()

        assert re.compile("^Elapsed time @.*$").match(caplog.records[0].msg)


def test_IgnoredChainedCallLogger(caplog):
    obj = IgnoredChainedCallLogger()

    with mltraq.options.option_context({"log.stdout": True}):
        init_logging()

        try:
            print(obj._ipython_canary_method_should_not_exist_)
        except AttributeError:
            pass

        assert obj._repr_html_() == ""
        assert obj.__str__() == ""

        with caplog.at_level(logging.ERROR):
            # Calling something, will trigger an error message on the logger
            obj.something()
            assert re.compile("^Ignoring chained operation: .something.*$").match(caplog.records[0].msg)


def test_KeyBoardInterrupt_catch_exceptions(caplog):
    with caplog.at_level(logging.ERROR):
        with mltraq.options.option_context({"log.stdout": True, "log.catch_exceptions": True}):
            init_logging()

            @default_exception_handler
            def nothing():
                raise KeyboardInterrupt

            nothing()

            assert re.compile("^Keyboard interrupt.$").match(caplog.records[0].msg)
