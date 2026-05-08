import sys
import subprocess
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                               QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
                               QComboBox, QMessageBox, QFileDialog, QSplitter)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QDragLeaveEvent, QPixmap, QFont
from pathlib import Path
from pathlib import Path


 
# Application -> What is running
# Window -> The Actual Window
# Widget -> A container within the window, or an interactable
# Layout -> The layout applied to a widget
# Label -> Text



# 1. Get the directory of the current script
current_dir = Path(__file__).resolve().parent

input_file_path = current_dir.parent / "scanner" / "input.txt"
scanner_file_path = current_dir.parent / "scanner" / "scanner.exe"
tokens_file_path = current_dir.parent / "scanner" / "tokens.txt"
parser_file_path = current_dir.parent / "parser" / "parser.py"
output_file_path = current_dir.parent / "output" / "ast_output.png"
easter_egg_path = current_dir.parent / "Doom" / "uzdoom.exe"


class FileDropTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent) # Inherit from QTextEdit
        self.setAcceptDrops(True) # Allows for Drag and Drop
        self.setPlaceholderText("Type text, drag a .txt file, or click 'Browse'...")

    def _returnFilePath(self, event):
        """
        Helper method to check if the dragged item is a local .txt file.
        Returns the file path as a string if valid, otherwise returns None.
        """
        mime = event.mimeData()
        # Two checks:
        # First check if data claims to have URLs (Fast)
        # Second check if the data actually does have URLs, so that we can retrieve them (slow)
        # We keep first check for performance reasons, and the second check to avoid errors
        if mime.hasUrls() and mime.urls(): 
            url = mime.urls()[0]
            if url.isLocalFile():
                return url.toLocalFile()
        return None

    def dragEnterEvent(self, event):
        # Function for when file is dragged into text box
        # If data has a URL and if that URL points to a local txt file
        file_path = self._returnFilePath(event)

        if file_path is None:
             # Default drag behavior. Allows for standard plain text to be directly dragged:
            super().dragEnterEvent(event)
        elif file_path.lower().endswith('.txt'):
            # Accepts data if file is of type .txt
            event.acceptProposedAction()
        else:
            # Rejects non-.txt files
            event.rejectProposedAction()


    def dropEvent(self, event):
        # If text file, try to read it to the text edit
        # Otherwise go to default behavior
        file_path = self._returnFilePath(event)

        if file_path is None:
             # Fall back to default drop behavior if it wasn't our handled file drop
            super().dropEvent(event)

        if file_path.lower().endswith('.txt'): 
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.setPlainText(file.read())
                
                event.acceptProposedAction()
                
                # Force the QTextEdit to clean up the visual drop cursor
                super().dragLeaveEvent(QDragLeaveEvent())
                return
                
            except Exception as e:
                self.setPlainText(f"Error reading file: {e}")
                event.acceptProposedAction()
                
                # Force the QTextEdit to clean up the visual drop cursor in case of an error
                super().dragLeaveEvent(QDragLeaveEvent()) 
                return
        else:
            # Rejects non-.txt files
            event.rejectProposedAction()

class ImageDisplayWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set some default visual properties
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(300, 300)

    def load_image_from_file(self, file_path):
        """Loads an image from the given path and displays it."""
        # 1. Create a QPixmap from the file path
        pixmap = QPixmap(file_path)
        
        # 2. Check if the image successfully loaded (e.g., file exists and is a valid image)
        if pixmap.isNull():
            self.setText(f"Failed to load image:\n{file_path}")
            return
            
        # 3. (Optional) Scale the image to fit the widget while maintaining aspect ratio
        # We constrain it to the current size of the label so it doesn't blow up the window
        scaled_pixmap = pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 4. Apply the pixmap to the label
        self.setPixmap(scaled_pixmap)

            
# Windows API Constants
GWL_STYLE = -16
WS_VISIBLE = 0x10000000
WS_CHILD = 0x40000000
WS_CLIPCHILDREN = 0x02000000

DOOM_WINDOW_TITLE = "The Ultimate Doom"                 # The EXACT title of the game window


class DoomContainerWidget(QWidget):
    """A custom widget specifically designed to hold the native Doom window."""
    def __init__(self):
        super().__init__()
        self.doom_hwnd = None
        self.setStyleSheet("background-color: black;")

    def resizeEvent(self, event):
        """Automatically called by PyQt whenever the window changes size."""
        super().resizeEvent(event)
        
        # If Doom is running, force it to match the new size of this widget
        if self.doom_hwnd:
            user32 = ctypes.windll.user32
            user32.MoveWindow(self.doom_hwnd, 0, 0, self.width(), self.height(), True)


class DoomApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Embedded Native Doom")
        self.resize(800, 600)

        # 1. Setup the UI layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.launch_doom()

        # Create our custom container widget and add it to the layout
        self.container = DoomContainerWidget()
        self.layout.addWidget(self.container)

        # Setup a background timer to wait for the Doom window to open
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_doom_window)

    def launch_doom(self):        
        # Launch the executable in the background
        subprocess.Popen([easter_egg_path])
        
        # Start checking for the window every 200 milliseconds
        self.timer.start(200)

    def check_for_doom_window(self):
        user32 = ctypes.windll.user32
        
        # Ask Windows if the game has successfully spawned its window yet
        doom_hwnd = user32.FindWindowW(None, DOOM_WINDOW_TITLE)

        if doom_hwnd:
            # The game window exists! Stop polling.
            self.timer.stop()
            
            # Save the handle to our container widget
            self.container.doom_hwnd = doom_hwnd

            # Get the Windows OS Handle (HWND) of the PyQt container widget
            # winId() returns a sip.voidptr, so we cast it to an integer
            pyqt_hwnd = int(self.container.winId())

            # 1. Reparent the Doom window to the PyQt widget
            user32.SetParent(doom_hwnd, pyqt_hwnd)

            # 2. Strip away the Windows Title Bar and Borders from the Doom Window
            user32.SetWindowLongPtrW(doom_hwnd, GWL_STYLE, WS_VISIBLE | WS_CHILD | WS_CLIPCHILDREN)

            # 3. Trigger an initial resize so it fits perfectly
            user32.MoveWindow(doom_hwnd, 0, 0, self.container.width(), self.container.height(), True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.easterEggCount = 0

        self.resultWindow = None

        self.setWindowTitle("Text & File Input Example")
        
        # Create and Set up Container for Window Content
        contentContainer = QWidget() 
        self.setCentralWidget(contentContainer)
        layout = QVBoxLayout(contentContainer)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(10)
        
        # Text Area
        self.text_input = FileDropTextEdit()

         # Browse Files Button
        self.browse_button = QPushButton("Browse for .txt Files")
        self.browse_button.clicked.connect(self.open_file_dialog)

        # Compile Button
        self.compile_button = QPushButton("Compile")
        self.compile_button.clicked.connect(self.compile)
        
        # Add Widgets to the layout
        layout.addWidget(self.text_input)
        layout.addSpacing(20)
        layout.addWidget(self.browse_button)
        layout.addSpacing(-5)
        layout.addWidget(self.compile_button)

        self.showMaximized()

    def open_file_dialog(self):
        # Open the file dialog
        # The arguments are: parent, dialog title, default directory, file filters
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Text File",
            "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        # If the user selected a file (didn't click cancel)
        if file_path:
            try:
                # Open, read, and display the file contents
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    self.text_input.setPlainText(file_content)
            except Exception as e:
                self.text_input.setPlainText(f"Error reading file: {e}")
        
    def save_file(self):
        try:
            # Get plain text from the widget
            content = self.text_input.toPlainText()
            
            # Write to the file using standard Python I/O
            with open(input_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error saving file: {e}")

        

    # Compiles code and opens new window to display tree
    def compile(self):
        if self.text_input.toPlainText().lower() == "hurt me plenty":
            self.resultWindow = DoomApp()
            self.resultWindow.show()
            return
            
        try:
            # Save File
            self.save_file()
            print("file saved")

            # =======================
            # Run Scanner
            # =======================
            try:
                result = subprocess.run(
                    [scanner_file_path],
                    cwd=scanner_file_path.parent,
                    capture_output=True,
                    text=True,
                    check=True
                )

                print("Scanner Output\n===========================")
                print(result.stdout)
                print("scanner.exe finished successfully")

            except Exception as e:

                print("Error while running scanner.exe")
                raise Exception(e.stderr)
            
            # =======================
            # Run parser            
            # =======================
            try:
                result = subprocess.run(
                    [sys.executable, parser_file_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("Parser Output\n===========================")
                print(result.stdout)
                print("Parser finished successfully!")


            except Exception as e:
                print("Error while running parser.py")
                raise Exception(e.stdout)

            # =======================
            # Open Result Window
            # =======================
            try:

                self.resultWindow = ResultWindow()
                self.resultWindow.show()
                print("image display\n")

            except Exception as e:

                print("Failed to open Result Window")
                print(str(e))
                raise

        except Exception as e:

            QMessageBox.information(self, 'Compile Error', str(e))
            print("Compile error:")
            print(str(e))

        

class ResultWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analysis Results")

        # 1. Main Container & Layout Setup
        container = QWidget()
        self.setCentralWidget(container)
        
        # Adding margins and spacing for a cleaner look
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 2. Top Control Bar (Combobox to select view)
        control_layout = QHBoxLayout()
        
        view_label = QLabel("Select View:")
        view_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Both", "Tree Only", "Tokens Only"])
        self.view_combo.setFont(QFont("Arial", 10))
        self.view_combo.setCursor(Qt.PointingHandCursor)

        # Connect combo box change event to our view toggler method
        self.view_combo.currentTextChanged.connect(self.update_view)
        
        control_layout.addWidget(view_label)
        control_layout.addWidget(self.view_combo)
        control_layout.addStretch() # Pushes the combo box to the left
        layout.addLayout(control_layout)

        # 3. Main Content Splitter (Allows resizing between image and text)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(4)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #bbb; border-radius: 2px; }")
        
        # Setup Image Viewer
        self.image_viewer = ImageDisplayWidget()
        self.image_viewer.load_image_from_file(output_file_path)

        # Setup Token Viewer (TextEdit)
        self.token_viewer = QTextEdit()
        self.token_viewer.setReadOnly(True)
        self.token_viewer.setFont(QFont("Consolas", 11)) # Monospace font for tokens
        self.token_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                line-height: 1.5;
            }
        """)
        self.load_tokens_file()

        # Add both to the splitter layout
        self.splitter.addWidget(self.image_viewer)
        self.splitter.addWidget(self.token_viewer)
        
        # Default distribution is 50/50 space
        self.splitter.setSizes([600, 600])

        layout.addWidget(self.splitter)
        
        self.close_button = QPushButton("Return to Main Menu")
        self.close_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545; /* Nice red color */
                color: white;
                padding: 5px 15px;
                border: none;
                border-r
                adius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)

        self.close_button.clicked.connect(self.close)
        control_layout.addWidget(self.close_button)


        # Force UI into default state based on combobox
        self.update_view(self.view_combo.currentText())

        self.showMaximized()

    def load_tokens_file(self):
        """Safely loads the tokens file into the text edit."""
        if tokens_file_path.exists():
            try:
                with open(tokens_file_path, "r", encoding="utf-8") as f:
                    self.token_viewer.setPlainText(f.read())
            except Exception as e:
                self.token_viewer.setPlainText(f"Error reading file: {e}")
        else:
            self.token_viewer.setPlainText(f"File not found:\n{tokens_file_path}\n\nWaiting for scanner output...")

    def update_view(self, mode):
        """Hides/Shows the widgets based on combobox selection."""
        if mode == "Both":
            self.image_viewer.show()
            self.token_viewer.show()
        elif mode == "Tree Only":
            self.image_viewer.show()
            self.token_viewer.hide()
        elif mode == "Tokens Only":
            self.image_viewer.hide()
            self.token_viewer.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
