APP_STYLESHEET = """
QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    color: #1d2939;
}
QMainWindow {
    background: #f5f7fb;
}
QFrame#sidebar {
    background: #0f172a;
    border-radius: 12px;
}
QListWidget#menu {
    background: transparent;
    border: none;
    color: #e2e8f0;
    padding: 8px;
}
QListWidget#menu::item {
    margin: 6px;
    padding: 12px;
    border-radius: 10px;
}
QListWidget#menu::item:selected {
    background: #2563eb;
    color: white;
}
QGroupBox {
    border: 1px solid #d0d7e2;
    border-radius: 12px;
    margin-top: 10px;
    background: #ffffff;
    padding: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: #0f172a;
    font-weight: 600;
}
QPushButton {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
}
QPushButton:hover {
    background: #1d4ed8;
}
QLineEdit, QTextEdit, QListWidget, QComboBox, QDateEdit, QTableWidget {
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: white;
    padding: 6px;
}
QLabel#title {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
}
"""
