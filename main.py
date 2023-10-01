import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
import speech_recognition as sr
import os
import webbrowser
from datetime import datetime


class CommandRecognizer(QThread):
    commandRecognized = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.keep_running = True

    def run(self):
        while self.keep_running:
            command = self.recognize_command()
            if self.keep_running:  # Check again before emitting the signal
                self.commandRecognized.emit(command)

    def recognize_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
            command = ""
            try:
                command = r.recognize_google(audio)
            except sr.UnknownValueError:
                return "Sorry, I didn't catch that. Try again."
            except sr.RequestError:
                return "API unavailable. Try again later."
            return command.lower()

    def stop_recognizing(self):
        self.keep_running = False


class Appy(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Appy')
        self.setLayout(QVBoxLayout())

        self.commandOutput = QTextEdit(self)
        self.commandOutput.setReadOnly(True)
        self.layout().addWidget(self.commandOutput)

        # Listen Button
        self.listenButton = QPushButton('Listen', self)
        self.listenButton.clicked.connect(self.start_listening)
        self.layout().addWidget(self.listenButton)

        # Stop Button
        self.stopButton = QPushButton('Stop', self)
        self.stopButton.clicked.connect(self.stop_listening)
        self.stopButton.setEnabled(False)
        self.layout().addWidget(self.stopButton)

        # Exit Button
        self.exitButton = QPushButton('Exit', self)
        self.exitButton.clicked.connect(self.exit_application)
        self.layout().addWidget(self.exitButton)

        self.recognizerThread = CommandRecognizer()
        self.recognizerThread.commandRecognized.connect(self.on_command_recognized)

    def start_listening(self):
        self.commandOutput.append("Listening...")
        self.listenButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.recognizerThread.keep_running = True
        self.recognizerThread.start()

    def stop_listening(self):
        self.recognizerThread.stop_recognizing()
        self.listenButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.commandOutput.append("Stopped listening.")

    def on_command_recognized(self, command):
        self.commandOutput.append(f"You said: {command}")
        if command not in ["Sorry, I didn't catch that. Try again."]:
            if "stop" in command:
                self.stop_listening()
            elif "close" in command:
                self.exit_application()
            else:
                self.execute_command(command)

    def execute_command(self, command):
        if 'search' in command:
            query = command.replace('search', '').strip()
            webbrowser.open(f'https://www.google.com/search?q={query}')
        elif 'play' in command:
            song = command.replace('play', '').strip()
            webbrowser.open(f'https://www.youtube.com/results?search_query={song}')
        elif 'time' in command:
            current_time = datetime.now().strftime('%H:%M:%S')
            self.commandOutput.append(f"Current Time: {current_time}")
        elif 'open calculator' in command:
            os.system('calc.exe')
        elif 'open google' in command or 'open chrome' in command:
            os.system('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"')
        else:
            self.commandOutput.append(f"'{command}' is not a recognized command. Try again.")

    def exit_application(self):
        self.commandOutput.append("Exiting Appy. Goodbye!")
        QApplication.instance().quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Appy()
    demo.show()
    sys.exit(app.exec())
