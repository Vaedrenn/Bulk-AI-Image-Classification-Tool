from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QMainWindow, QTabWidget

from src.gui.main_window import MainWindow


def test_main_window_display(qtbot):
    """Test if the main window displays correctly."""
    window = MainWindow()
    window.setGeometry(100, 100, 1200, 800)
    window.setWindowTitle("Bulk AI Image Classification Tool")

    # Use qtbot to simulate interaction and wait for the window to be shown
    qtbot.addWidget(window)
    # Check if the window title is set correctly
    assert window.windowTitle() == "Bulk AI Image Classification Tool"

    # Check if the window geometry is set correctly
    assert window.geometry() == QRect(100, 100, 1200, 800)


def test_main_window_initialization(qtbot):
    """Test if the main window is initialized correctly."""
    # Create the main window, not to be confused with QMainWindow
    main_window = MainWindow()

    # Verify that the main window is an instance of QMainWindow
    assert isinstance(main_window, QMainWindow)

    # Verify that the central widget is a QTabWidget
    central_widget = main_window.centralWidget()
    assert isinstance(central_widget, QTabWidget)

    # Verify that the tab widget contains the expected number of tabs
    assert central_widget.count() == 2

    # Verify that the tab titles are set correctly
    assert central_widget.tabText(0) == "Main"
    assert central_widget.tabText(1) == "File Manager"
