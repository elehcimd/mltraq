from pprint import pprint

from mltraq.utils.sysenv import get_sysenv_info


def test_environment():
    """
    Test: we can track the environment setup.
    """

    env = get_sysenv_info()
    print("--")
    pprint(env, depth=4)
    print("--")
    assert len(env.platform.machine) > 0
    assert env.sysmon_stats.cpu_cnt > 0
    assert env.sysmon_stats.mem_total_gb > 0
    assert env.sysmon_stats.disk_total_gb > 0
