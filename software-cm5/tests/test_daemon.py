from supervisor import __version__
from supervisor.daemon import SupervisorDaemon


def test_package_version():
    assert __version__ == "0.1.0"


def test_daemon_initialization():
    daemon = SupervisorDaemon(port="/dev/ttyAMA0", baudrate=115200)
    assert daemon.port == "/dev/ttyAMA0"
    assert daemon.baudrate == 115200
    assert not daemon.is_running
