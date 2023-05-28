from PySide6.QtCore import Signal, QObject

class Logger(QObject):
    log_signal = Signal(str)
    finished_signal = Signal()  # New signal

    def log(self, message):
        self.log_signal.emit(message)

    def finished(self):  # New method
        self.finished_signal.emit()
