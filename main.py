import os
from PySide6.QtWidgets import QApplication, QFileDialog, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QTextEdit, QLabel
from PySide6.QtCore import Qt
from converter import convert_java_directory_to_ts
from Logger import Logger

app = QApplication([])
window = QWidget()
main_layout = QVBoxLayout(window)

source_folder_label = QLabel("Source Folder: None")
target_folder_label = QLabel("Target Folder: None")

java_directory = ""
ts_directory = ""

progress = QProgressBar()
main_layout.addWidget(progress)

# Function to set progress to max when conversion is complete
def complete_conversion():
    progress.setValue(progress.maximum())

def log_message(message):
    log_output.append(message)
    progress.setValue(progress.value() + 1)

def choose_source_folder():
    global java_directory
    java_directory = QFileDialog.getExistingDirectory()
    source_folder_label.setText(f"Source Folder: {java_directory}")

def choose_target_folder():
    global ts_directory
    ts_directory = QFileDialog.getExistingDirectory()
    target_folder_label.setText(f"Target Folder: {ts_directory}")

def convert():
    if not java_directory or not ts_directory:
        log_output.append("Please choose both source and target directories before converting.")
        return
        
    files = [f for f in os.listdir(java_directory) if f.endswith(".java")]
    progress.setMaximum(len(files))
    progress.setValue(0)
    convert_java_directory_to_ts(java_directory, ts_directory, logger)

folder_selection_layout = QHBoxLayout()

source_button = QPushButton('Choose Source Folder')
source_button.clicked.connect(choose_source_folder)
folder_selection_layout.addWidget(source_button)

target_button = QPushButton('Choose Target Folder')
target_button.clicked.connect(choose_target_folder)
folder_selection_layout.addWidget(target_button)

convert_button = QPushButton('Convert')
convert_button.clicked.connect(convert)
folder_selection_layout.addWidget(convert_button)

main_layout.addLayout(folder_selection_layout)

main_layout.addWidget(source_folder_label)
main_layout.addWidget(target_folder_label)

log_output = QTextEdit()
log_output.setReadOnly(True)
main_layout.addWidget(log_output)

logger = Logger()
logger.log_signal.connect(log_message)
logger.finished_signal.connect(complete_conversion)  # Connect the new signal

window.show()
app.exec_()
