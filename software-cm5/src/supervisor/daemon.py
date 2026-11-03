"""Módulo principal do daemon de supervisão no Raspberry Pi CM5."""


class SupervisorDaemon:
    """Daemon de supervisão responsável por heartbeat, arme e UART com o RP2040."""

    def __init__(self, port: str = "/dev/ttyAMA0", baudrate: int = 115200) -> None:
        self.port = port
        self.baudrate = baudrate
        self.is_running = False

    def start(self) -> None:
        """Inicia os loops de supervisão."""
        self.is_running = True

    def stop(self) -> None:
        """Para os loops de supervisão e coloca saídas em estado seguro."""
        self.is_running = False
