import os
import GUI
import sys
import shutil
import atexit
import PyPDF2
import pyttsx3
import media_player as mp
from tempfile import NamedTemporaryFile


class PdfToAudio:
    """
    A class to convert PDF documents to audio using PyQt5 for the GUI.

    Attributes:
        main_window (GUI.Window): The main window of the application.
        speech (str): The file path of the generated speech audio.
        media_player (mp.MediaPlayer): The media player instance.
    """

    def __init__(self, width, height):
        """
        Initialize the PdfToAudio application.

        :param width: Width of the main window.
        :param height: Height of the main window.
        """
        self.main_window = GUI.Window(width, height, 'Pdf to Audio', (18, 63, 79),icon='assets/img/icon.png', titlebar=True)
        self.speech = None

        self.loadUI()

    def loadUI(self):
        """
        Load the user interface for the application.
        """
        self.main_layout = GUI.Layout(self.main_window.central, 'main_layout', 'h')

        self.toolbar_layout = GUI.Layout(None, 'toolbar_layout', 'h')
        self.main_window.enable_toolbar(self.toolbar_layout.background_widget, (255, 127, 80))

        GUI.ToolButton(self.toolbar_layout, 'Open', tooltip='Open pdf file', action=self.load_pdf)
        GUI.ToolButton(self.toolbar_layout, 'Save', tooltip='Save audio file', action=self.save_audio)
        self.toolbar_layout.layout.addStretch(1)
        GUI.ToolButton(self.toolbar_layout, 'Close', action=self.close)

        self.media_player = mp.MediaPlayer()
        self.media_player_layout = GUI.Layout(self.main_layout, 'media_player_layout', 'h')
        self.media_player.load_ui(self.media_player_layout, 'basic')

    def run(self):
        """
        Run the main event loop of the application.
        """
        self.main_window.show()
        self.main_window.app.exec_()

    def close(self):
        """
        Close the application.
        """
        sys.exit()

    def load_pdf(self):
        """
        Load a PDF file and convert it to audio.
        """
        file_name, _ = GUI.QFileDialog.getOpenFileName(caption="Open PDF", directory="",
                                                       filter="PDF Files (*.pdf);")
        file_path = GUI.Widget.check_path(GUI.Widget, path=file_name, type='pdf')
        if file_path:
            self.pdf_to_audio(file_path)

    def save_audio(self):
        """
        Save the generated audio to a file.
        """
        file_name, _ = GUI.QFileDialog.getSaveFileName(caption='Save audio',
                                                       directory=self.media_player.track_name if self.media_player.track_name is not None else '',
                                                       filter="Audio Files (*.mp3 *.wav);")
        if self.media_player.track is not None:
            shutil.copy(self.speech, file_name)

    def pdf_to_audio(self, pdf_path):
        """
        Convert a PDF file to audio.

        :param pdf_path: Path to the PDF file.
        """
        text = self.extract_text(pdf_path)
        file_name = str(pdf_path).split('.')[-2].split('\\')[-1]
        self.speech = self.text_to_speech(text)
        self.media_player.load_audio(file=self.speech, file_name=file_name)

    def extract_text(self, pdf_path):
        """
        Extract text from a PDF file.

        :param pdf_path: Path to the PDF file.
        :return: Extracted text.
        """
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text

    def text_to_speech(self, text):
        """
        Convert text to speech and save it as an audio file.

        :param text: Text to convert to speech.
        :return: File path of the generated speech audio.
        """
        engine = pyttsx3.init()
        with NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
            temp_file.close()
            engine.save_to_file(text, temp_filename)
            engine.runAndWait()
            atexit.register(self.cleanup_tempfile, temp_filename)
        return temp_filename

    def cleanup_tempfile(self, temp_filename):
        """
        Clean up the temporary audio file.

        :param temp_filename: Path to the temporary file.
        """
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    def __del__(self):
        """
        Destructor to clean up temporary files and resources.
        """
        if GUI.Widget.check_path(GUI.Widget, 'assets/temp', 'folder'):
            shutil.rmtree('assets\\temp', True)


if __name__ == '__main__':
    PTA = PdfToAudio(400, 200)
    PTA.run()