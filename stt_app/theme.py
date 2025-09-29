from PySide6 import QtCore, QtGui, QtWidgets


def apply_dark_theme(app: QtWidgets.QApplication) -> None:
    """Apply a modern dark theme to the Qt application.
    
    Professional dark design with high contrast and clean appearance.
    """
    # Modern dark palette
    palette = QtGui.QPalette()
    dark_bg = QtGui.QColor(18, 18, 18)
    darker_bg = QtGui.QColor(24, 24, 24)
    border = QtGui.QColor(45, 45, 45)
    text = QtGui.QColor(240, 240, 240)
    text_secondary = QtGui.QColor(160, 160, 160)
    accent_blue = QtGui.QColor(66, 135, 245)
    
    palette.setColor(QtGui.QPalette.Window, darker_bg)
    palette.setColor(QtGui.QPalette.WindowText, text)
    palette.setColor(QtGui.QPalette.Base, dark_bg)
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(32, 32, 32))
    palette.setColor(QtGui.QPalette.ToolTipBase, darker_bg)
    palette.setColor(QtGui.QPalette.ToolTipText, text)
    palette.setColor(QtGui.QPalette.Text, text)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(40, 40, 40))
    palette.setColor(QtGui.QPalette.ButtonText, text)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Highlight, accent_blue)
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.PlaceholderText, text_secondary)

    app.setPalette(palette)

    # Professional dark stylesheet
    qss = """
    /* Global styles */
    QWidget { 
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 10pt; 
        color: #f0f0f0;
    }
    
    QMainWindow, QDialog { 
        background-color: #181818; 
    }
    
    QLabel { 
        color: #f0f0f0; 
    }

    /* Header bar */
    #headerBar { 
        background-color: #1a1a1a; 
        border-bottom: 1px solid #2d2d2d;
        padding: 8px 0px;
    }
    
    #headerBar QLabel { 
        font-size: 18pt; 
        font-weight: 600; 
        color: #ffffff;
        letter-spacing: -0.5px;
    }

    /* Status pill */
    QLabel[type="pill"] { 
        background-color: #282828; 
        border: 1px solid #3d3d3d; 
        border-radius: 12px; 
        padding: 6px 16px; 
        color: #d0d0d0;
        font-weight: 500;
        font-size: 9pt;
    }

    /* Input fields */
    QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #1a1a1a; 
        border: 1.5px solid #3d3d3d; 
        border-radius: 10px; 
        padding: 10px 14px;
        selection-background-color: #4287f5;
        font-size: 10pt;
        color: #f0f0f0;
    }
    
    QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border: 2px solid #4287f5;
        padding: 9px 13px;
    }

    /* Buttons */
    QPushButton { 
        background-color: #282828; 
        border: 1.5px solid #3d3d3d; 
        border-radius: 12px; 
        padding: 12px 24px;
        font-weight: 500;
        font-size: 10pt;
        color: #f0f0f0;
    }
    
    QPushButton:hover { 
        background-color: #323232;
        border-color: #4d4d4d;
    }
    
    QPushButton:pressed { 
        background-color: #242424;
    }
    
    /* Primary button */
    QPushButton[type="primary"] { 
        background-color: #4287f5; 
        border: none; 
        color: #ffffff;
        font-weight: 600;
    }
    
    QPushButton[type="primary"]:hover { 
        background-color: #3a78db;
    }
    
    QPushButton[type="primary"]:pressed { 
        background-color: #2f63b8;
    }
    
    /* Danger button */
    QPushButton[type="danger"] { 
        background-color: #3d2020; 
        border: 1.5px solid #5d3030; 
        color: #ff6b6b;
        font-weight: 500;
    }
    
    QPushButton[type="danger"]:hover { 
        background-color: #4d2828;
        border-color: #7d4040;
    }
    
    QPushButton[type="danger"]:pressed { 
        background-color: #331818;
    }

    /* Progress bar */
    QProgressBar { 
        border: 1.5px solid #3d3d3d; 
        border-radius: 10px; 
        text-align: center; 
        background: #1a1a1a; 
        height: 20px;
        color: #f0f0f0;
        font-weight: 500;
    }
    
    QProgressBar::chunk { 
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #34c759, stop:1 #30d158);
        border-radius: 9px;
    }

    /* List widget */
    QListWidget { 
        background-color: #1a1a1a; 
        border: 1.5px solid #3d3d3d; 
        border-radius: 12px;
        padding: 8px;
        outline: none;
    }
    
    QListWidget::item {
        border-radius: 8px;
        padding: 10px;
        margin: 2px 0px;
        color: #f0f0f0;
    }
    
    QListWidget::item:hover {
        background-color: #242424;
    }
    
    QListWidget::item:selected {
        background-color: #4287f5;
        color: #ffffff;
    }

    /* Context menus */
    QMenu { 
        background-color: #1a1a1a; 
        border: 1px solid #3d3d3d;
        border-radius: 10px;
        padding: 6px;
    }
    
    QMenu::item {
        padding: 8px 20px;
        border-radius: 6px;
        color: #f0f0f0;
    }
    
    QMenu::item:selected { 
        background-color: #4287f5;
        color: #ffffff;
    }
    
    /* Dialog buttons */
    QDialogButtonBox QPushButton {
        min-width: 80px;
        padding: 10px 20px;
    }
    
    /* Checkboxes */
    QCheckBox {
        spacing: 8px;
        font-weight: 500;
        color: #f0f0f0;
    }
    
    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border-radius: 6px;
        border: 2px solid #3d3d3d;
        background-color: #1a1a1a;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4287f5;
        border-color: #4287f5;
    }
    
    /* Spinbox buttons */
    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        background-color: transparent;
        border: none;
        width: 20px;
    }
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #242424;
    }
    
    /* Combobox */
    QComboBox::drop-down {
        border: none;
        width: 30px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #1a1a1a;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        selection-background-color: #4287f5;
        selection-color: #ffffff;
        outline: none;
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        background: transparent;
        width: 12px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background: #3d3d3d;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #4d4d4d;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background: transparent;
        height: 12px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background: #3d3d3d;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: #4d4d4d;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    """
    app.setStyleSheet(qss)