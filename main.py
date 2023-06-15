from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QLineEdit, QTextEdit
import sys
from converter import convert_java_to_ts, convert_java_directory_to_ts
from Logger import Logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.source_directory = None
        self.destination_directory = None
        self.prefixType = '@type2' # Default prefixType

        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        folder_selection_layout = QHBoxLayout()


        # Prefix type input field
        self.prefixType_input = QLineEdit(self.prefixType)
        h_layout.addWidget(QLabel("Prefix"))
        h_layout.addWidget(self.prefixType_input)

        # Create QWidget to contain the QHBoxLayout
        h_widget = QWidget()
        h_widget.setLayout(h_layout)
        layout.addWidget(h_widget)

        self.source_button = QPushButton("Source 폴더 선택")
        self.source_button.clicked.connect(self.select_source)
        folder_selection_layout.addWidget(self.source_button)

        self.destination_button = QPushButton("Destination 폴더 선택")
        self.destination_button.clicked.connect(self.select_destination)
        folder_selection_layout.addWidget(self.destination_button)

        self.convert_button = QPushButton("변환하기")
        self.convert_button.clicked.connect(self.start_conversion)
        folder_selection_layout.addWidget(self.convert_button)

        layout.addLayout(folder_selection_layout)

        self.source_label = QLabel("Source 폴더를 선택하세요")
        layout.addWidget(self.source_label)

        self.destination_label = QLabel("Destination 폴더를 선택하세요")
        layout.addWidget(self.destination_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        

        central_widget = QWidget()
        central_widget.setLayout(layout)

        # central_widget.setFixedWidth(300)
        # central_widget.setFixedHeight(300)

        self.setCentralWidget(central_widget)


        self.logger = Logger()
        self.logger.log_signal.connect(self.log_message)

    def log_message(self, message):
        self.log_output.append(message)

    def select_source(self):
        self.source_directory = QFileDialog.getExistingDirectory()
        self.source_label.setText(f"Source 폴더: {self.source_directory}")

    def select_destination(self):
        self.destination_directory = QFileDialog.getExistingDirectory()
        self.destination_label.setText(f"Destination 폴더: {self.destination_directory}")

    def start_trans(self):
        self.log_output.setText('작업시작')

    def finish_trans(self):
        self.log_output.setStyleSheet("background-color: #00B050;")
        self.log_output.setText('작업완료')

    def start_conversion(self):
        # Here you should call the function that will do the actual conversion
        # from Java to TypeScript
        # self.start_trans()
        print("Starting conversion...")

        self.prefixType = self.prefixType_input.text() or '@type2' # Get prefixType from input field
        convert_java_directory_to_ts(self.source_directory, self.destination_directory, self.logger, self.prefixType)
        
        # self.finish_trans()
        print("Conversion completed.")


app = QApplication(sys.argv)
window = MainWindow()

window.show()
app.exec_()
