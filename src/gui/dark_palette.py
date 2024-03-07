from PyQt5.QtGui import QPalette, QColor


def create_dark_palette():
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.ToolTipText, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.Text, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(250, 250, 250))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(250, 250, 250))

    dark_palette.setColor(QPalette.Background, QColor(45, 45, 45))

    return dark_palette
