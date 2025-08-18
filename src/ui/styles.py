# Основные цвета приложения
PRIMARY_COLOR = "#4A6FA5"  # Приглушенный синий
SECONDARY_COLOR = "#6B8CBE"  # Светлее основной
ACCENT_COLOR = "#FF7E5F"  # Теплый оранжево-красный
BACKGROUND_COLOR = "#fcfcfc"  # Светло-серый фон
TEXT_COLOR = "#333333"  # Темно-серый для текста
LIGHT_TEXT = "#FFFFFF"  # Белый текст
DARK_BORDER = "#D1D9E6"  # Светлая граница

# Стиль главного окна
MAIN_WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {BACKGROUND_COLOR};
    }}
    QWidget {{
        color: {TEXT_COLOR};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
"""

# Кнопки режимов
VIDEO_MODE_BUTTON = f"""
    QPushButton {{
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 500;
        background: {PRIMARY_COLOR};
        color: {LIGHT_TEXT};
        border: none;
        border-top-left-radius: 6px;
        border-bottom-left-radius: 6px;
    }}
    QPushButton:checked {{
        background: {SECONDARY_COLOR};
        font-weight: 600;
    }}
    QPushButton:hover {{
        background: {SECONDARY_COLOR};
    }}
"""

SUBTITLE_MODE_BUTTON = f"""
    QPushButton {{
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 500;
        background: {ACCENT_COLOR};
        color: {LIGHT_TEXT};
        border: none;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }}
    QPushButton:checked {{
        background: #E56A4F;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background: #E56A4F;
    }}
"""

# Основные кнопки
PRIMARY_BUTTON = f"""
    QPushButton {{
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 500;
        background: {PRIMARY_COLOR};
        color: {LIGHT_TEXT};
        border-radius: 6px;
        min-height: 40px;
    }}
    QPushButton:hover {{
        background: {SECONDARY_COLOR};
    }}
    QPushButton:disabled {{
        background: #CCD4E1;
        color: #A0A8B5;
    }}
"""

ACCENT_BUTTON = f"""
    QPushButton {{
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 500;
        background: {ACCENT_COLOR};
        color: {LIGHT_TEXT};
        border-radius: 6px;
        min-height: 40px;
    }}
    QPushButton:hover {{
        background: #E56A4F;
    }}
    QPushButton:disabled {{
        background: #CCD4E1;
        color: #A0A8B5;
    }}
"""

# Поля ввода и выбора
INPUT_STYLE = f"""
    QComboBox, QTextEdit, QLineEdit {{
        padding: 8px 12px;
        font-size: 14px;
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        background: white;
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left-width: 1px;
        border-left-color: {DARK_BORDER};
        border-left-style: solid;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }}
"""

# Группы настроек
GROUP_BOX_STYLE = f"""
    QGroupBox {{
        font-size: 14px;
        font-weight: 500;
        border: 1px solid {DARK_BORDER};
        border-radius: 8px;
        margin-top: 16px;
        padding-top: 24px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
    }}
"""

# Вкладки
TAB_STYLE = f"""
    QTabWidget::pane {{
        border: 1px solid {DARK_BORDER};
        border-radius: 8px;
        padding: 8px;
        background: white;
    }}
    QTabBar::tab {{
        padding: 8px 16px;
        background: {BACKGROUND_COLOR};
        border: 1px solid {DARK_BORDER};
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 4px;
    }}
    QTabBar::tab:selected {{
        background: white;
        border-bottom: 1px solid white;
        margin-bottom: -1px;
    }}
"""

# Прогресс-бар
PROGRESS_BAR = f"""
    QProgressBar {{
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        text-align: center;
        height: 24px;
    }}
    QProgressBar::chunk {{
        background: {PRIMARY_COLOR};
        border-radius: 5px;
    }}
"""

# Предпросмотр видео
PREVIEW_LABEL = f"""
    background: #2C3E50;
    min-height: 300px;
    color: {LIGHT_TEXT}; 
    font-size: 16px;
    border-radius: 8px;
    padding: 20px;
"""

SHADOW_EFFECT = """
    QFrame, QGroupBox, QTabWidget::pane {
        border-radius: 8px;
        background-color: white;
        border: none;
    }
"""

BUTTON_HOVER_ANIMATION = """
    QPushButton {
        transition: background-color 0.3s ease;
    }
"""

FONT_STYLE = """
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QLabel {
        font-size: 14px;
    }
    QGroupBox {
        font-size: 15px;
        font-weight: 500;
    }
"""