# right_panel.py - Updated with readable font application
import weakref
import gc
import time
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGroupBox, 
                             QCheckBox, QScrollArea, QLabel, QMainWindow, QMessageBox, QHBoxLayout)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import QUrl, Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from config import load_config, save_config, get_config_value, set_config_value
from styles import get_icon_path, get_tool_urls
from font_loader import font_loader
import config


class ToolWindow(QMainWindow):
    def __init__(self, url, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"LostKit - {title}")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.setWindowFlags(Qt.WindowType.Window)
        
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        
        # Set black background
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        
        # Store tool name for persistent storage
        self.tool_name = title
        self.load_window_geometry()
        
        self.setMinimumSize(600, 400)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Use persistent profile names without process IDs or timestamps
        profile_name = f"ToolWindow_{title.replace(' ', '_')}"
        
        try:
            profile = QWebEngineProfile(profile_name, self)
            
            # Use persistent cache paths that survive application restarts
            cache_path = config.get_persistent_cache_path(f"tool_{title.replace(' ', '_')}")
            storage_path = config.get_persistent_profile_path(f"tool_{title.replace(' ', '_')}")
            
            print(f"Tool '{title}' using persistent cache: {cache_path}")
            print(f"Tool '{title}' using persistent storage: {storage_path}")
            
            profile.setCachePath(cache_path)
            profile.setPersistentStoragePath(storage_path)
            
            # Force persistent cookies for login state preservation
            profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            
            # Optimize settings while preserving login functionality
            settings = profile.settings()
            if get_config_value("resource_optimization", True):
                settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)

            page = QWebEnginePage(profile, self)
            self.web_view = QWebEngineView()
            self.web_view.setPage(page)
            
            # Store references but don't store temporary paths
            self.profile_name = profile_name
            self.cache_path = cache_path
            self.storage_path = storage_path
            self._profile = profile
            
        except Exception as e:
            print(f"Error creating web engine profile: {e}")
            self.web_view = QWebEngineView()
            self.profile_name = None
            self.cache_path = None
            self.storage_path = None
            self._profile = None
        
        layout.addWidget(self.web_view)
        
        print(f"Loading URL in tool window: {url}")
        self.web_view.setUrl(QUrl(url))
        
        # Setup cleanup timer
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.perform_cleanup)
        cleanup_interval = get_config_value("cache_cleanup_interval", 300) * 1000
        self.cleanup_timer.start(cleanup_interval)
        
        # Apply readable fonts after window creation
        QTimer.singleShot(100, self.force_apply_readable_fonts)

    def force_apply_readable_fonts(self):
        """Force apply readable fonts to tool window"""
        font = QFont()
        if font_loader.is_custom_font_available():
            font.setFamily(font_loader.get_font_family_name())
            print(f"Tool window using custom font: {font_loader.get_font_family_name()}")
        else:
            # Try to find Runescape-Quill-Caps specifically
            test_font = QFont("Runescape-Quill-Caps", 18)
            if test_font.exactMatch():
                font.setFamily("Runescape-Quill-Caps")
                print(f"Tool window using Runescape-Quill-Caps font")
            else:
                font.setFamily("Arial")
                print(f"Tool window using Arial fallback")
        
        font.setPointSize(18)  # Readable font for tool windows
        font.setWeight(QFont.Weight.Normal)
        
        self.setFont(font)
        print(f"Applied {font.pointSize()}pt font ({font.family()}) to tool window: {self.tool_name}")

    def load_window_geometry(self):
        """Load window geometry specific to this tool"""
        try:
            config_key = f"tool_window_geometry_{self.tool_name.replace(' ', '_')}"
            geom = get_config_value(config_key, None)
            
            if geom and isinstance(geom, list) and len(geom) == 4:
                x, y, w, h = [int(val) for val in geom]
                # Ensure window appears on screen
                x = max(0, min(x, 1920 - w))
                y = max(0, min(y, 1080 - h))
                w = max(600, min(w, 1920))
                h = max(400, min(h, 1080))
                self.setGeometry(x, y, w, h)
                print(f"Restored geometry for {self.tool_name}: {w}x{h} at ({x},{y})")
            else:
                # Default geometry with slight offset
                offset = hash(self.tool_name) % 10 * 25
                self.setGeometry(200 + offset, 200 + offset, 1000, 800)
                print(f"Using default geometry for {self.tool_name}")
        except (ValueError, TypeError) as e:
            print(f"Error setting tool window geometry: {e}, using defaults")
            self.setGeometry(200, 200, 1000, 800)

    def save_window_geometry(self):
        """Save window geometry specific to this tool"""
        try:
            geom = self.geometry()
            config_key = f"tool_window_geometry_{self.tool_name.replace(' ', '_')}"
            set_config_value(config_key, [geom.x(), geom.y(), geom.width(), geom.height()])
            print(f"Saved geometry for {self.tool_name}: {geom.width()}x{geom.height()}")
        except Exception as e:
            print(f"Error saving tool window geometry: {e}")

    def perform_cleanup(self):
        """Perform light cleanup without removing persistent data"""
        try:
            if get_config_value("resource_optimization", True):
                # Only memory cleanup, preserve login data
                gc.collect()
        except Exception as e:
            print(f"Error during tool window cleanup: {e}")

    def cleanup_cache_files(self):
        """Light cleanup - preserve login data and cookies"""
        print(f"Tool window '{self.tool_name}' cleanup: Preserving login data")
        # Don't delete persistent storage - it contains login sessions

    def resizeEvent(self, event):
        """Handle window resize events with debounced saving"""
        super().resizeEvent(event)
        if not hasattr(self, 'save_timer'):
            self.save_timer = QTimer(self)
            self.save_timer.setSingleShot(True)
            self.save_timer.timeout.connect(self.save_window_geometry)
        self.save_timer.start(1000)

    def moveEvent(self, event):
        """Handle window move events with debounced saving"""
        super().moveEvent(event)
        if not hasattr(self, 'save_timer'):
            self.save_timer = QTimer(self)
            self.save_timer.setSingleShot(True)
            self.save_timer.timeout.connect(self.save_window_geometry)
        self.save_timer.start(1000)

    def closeEvent(self, event):
        """Clean up when closing but preserve persistent data"""
        # Save geometry before closing
        self.save_window_geometry()
        
        if hasattr(self, 'cleanup_timer'):
            self.cleanup_timer.stop()
        
        # Clean up web view properly but preserve persistent storage
        if hasattr(self, 'web_view') and self.web_view:
            try:
                self.web_view.setPage(None)
                self.web_view.deleteLater()
            except Exception as e:
                print(f"Error cleaning up web view: {e}")
        
        # Don't clean persistent cache files - they contain login data
        print(f"Tool window '{self.tool_name}' closed - login data preserved")
        gc.collect()
        event.accept()


class InGameBrowser(QWidget):
    closed = pyqtSignal()
    
    def __init__(self, url, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.url = url
        self.title = title
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Use persistent profile for in-game browser tabs too
        profile_name = f"InGameBrowser_{title.replace(' ', '_')}"
        
        try:
            profile = QWebEngineProfile(profile_name, self)
            
            # Use persistent storage for in-game browsers too
            cache_path = config.get_persistent_cache_path(f"ingame_{title.replace(' ', '_')}")
            storage_path = config.get_persistent_profile_path(f"ingame_{title.replace(' ', '_')}")
                
            profile.setCachePath(cache_path)
            profile.setPersistentStoragePath(storage_path)
            profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            
            # Optimize for in-game browser
            settings = profile.settings()
            if get_config_value("resource_optimization", True):
                settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)

            page = QWebEnginePage(profile, self)
            self.web_view = QWebEngineView()
            self.web_view.setPage(page)
            
            # Store for reference
            self.profile_name = profile_name
            self.cache_path = cache_path
            self.storage_path = storage_path
            self._profile = profile
            
        except Exception as e:
            print(f"Error creating in-game browser profile: {e}")
            self.web_view = QWebEngineView()
            self.profile_name = None
            self.cache_path = None
            self.storage_path = None
            self._profile = None
        
        layout.addWidget(self.web_view)
        
        print(f"Loading URL in tab: {url}")
        self.web_view.setUrl(QUrl(url))

    def cleanup_cache_files(self):
        """Light cleanup - preserve login data"""
        print(f"In-game browser '{self.title}' cleanup: Preserving login data")
        # Don't delete persistent storage

    def closeEvent(self, event):
        """Clean up properly but preserve persistent data"""
        if hasattr(self, 'web_view') and self.web_view:
            try:
                self.web_view.setPage(None)
                self.web_view.deleteLater()
            except Exception as e:
                print(f"Error cleaning up web view: {e}")
        
        # Don't clean persistent storage
        self.closed.emit()
        event.accept()


class RightToolsPanel(QWidget):
    browser_requested = pyqtSignal(str, str)
    chat_toggle_requested = pyqtSignal()
    panel_collapse_requested = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config = load_config()
        self.tool_windows = weakref.WeakValueDictionary()
        self.window_count = 0
        
        # Restore collapse state
        self.collapsed = get_config_value("right_panel_collapsed", False)
        self.saved_width = self.config.get("right_panel_width", 250)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        
        # Calculate optimal panel width
        self.optimal_width = self.calculate_optimal_width()
        
        # Set fixed width based on restored collapse state
        if self.collapsed:
            self.setFixedWidth(25)
        else:
            self.setFixedWidth(self.optimal_width)
        
        self.setup_ui()
        
        # Apply readable fonts after UI creation
        QTimer.singleShot(100, self.force_apply_readable_fonts)
        
    def force_apply_readable_fonts(self):
        """Force apply readable fonts to all panel elements"""
        print("Forcing readable font application to right panel...")
        
        # Create readable fonts for different elements
        button_font = QFont()
        if font_loader.is_custom_font_available():
            button_font.setFamily(font_loader.get_font_family_name())
            print(f"Right panel using custom font: {font_loader.get_font_family_name()}")
        else:
            # Try to find Runescape-Quill-Caps specifically
            test_font = QFont("Runescape-Quill-Caps", 18)
            if test_font.exactMatch():
                button_font.setFamily("Runescape-Quill-Caps")
                print("Right panel using Runescape-Quill-Caps font")
            else:
                button_font.setFamily("Arial")
                print("Right panel using Arial fallback")
        
        button_font.setPointSize(18)  # Readable size for buttons
        button_font.setWeight(QFont.Weight.Normal)
        
        group_font = QFont()
        group_font.setFamily(button_font.family())
        group_font.setPointSize(20)  # Slightly larger for group titles
        group_font.setWeight(QFont.Weight.Bold)
        
        checkbox_font = QFont()
        checkbox_font.setFamily(button_font.family())
        checkbox_font.setPointSize(16)  # Readable size for checkboxes
        
        # Apply fonts to all elements recursively
        self.apply_fonts_to_children(self, button_font, group_font, checkbox_font)
        
        print(f"Applied readable fonts to right panel elements: buttons({button_font.pointSize()}pt), groups({group_font.pointSize()}pt), checkboxes({checkbox_font.pointSize()}pt)")
    
    def apply_fonts_to_children(self, widget, button_font, group_font, checkbox_font):
        """Apply appropriate readable fonts to all child widgets"""
        try:
            if isinstance(widget, QPushButton):
                widget.setFont(button_font)
            elif isinstance(widget, QGroupBox):
                widget.setFont(group_font)
            elif isinstance(widget, QCheckBox):
                widget.setFont(checkbox_font)
            else:
                widget.setFont(button_font)  # Default to button font
            
            # Apply to children
            for child in widget.findChildren(QWidget):
                self.apply_fonts_to_children(child, button_font, group_font, checkbox_font)
                
        except Exception as e:
            print(f"Error applying fonts: {e}")
        
    def calculate_optimal_width(self):
        """Calculate the optimal width to fit all buttons and scrollbar"""
        base_button_width = 160
        total_width = base_button_width + 16 + 23 + 8 + 10 + 16 + 8
        return total_width
        
    def setup_ui(self):
        """Setup UI based on current collapse state"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)
        
        if self.collapsed:
            self.setup_collapsed_ui(main_layout)
        else:
            self.setup_expanded_ui(main_layout)

    def setup_collapsed_ui(self, main_layout):
        """Setup UI for collapsed state"""
        self.clear_layout(main_layout)
        
        main_layout.addStretch()
        
        expand_container = QWidget()
        expand_container.setFixedHeight(40)
        expand_layout = QHBoxLayout(expand_container)
        expand_layout.setContentsMargins(0, 0, 2, 0)
        
        self.expand_btn = QPushButton("▶")
        self.expand_btn.setFixedSize(18, 35)
        self.expand_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b4a4a;
                border: 1px solid #2a2a2a;
                border-radius: 2px;
                color: #f5e6c0;
                font-weight: bold;
                font-size: 10px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #a55a5a;
                border-color: #8b4a4a;
            }
            QPushButton:pressed {
                background-color: #8b4a4a;
                border: 1px inset #2a2a2a;
            }
        """)
        self.expand_btn.clicked.connect(self.expand_panel)
        
        expand_layout.addStretch()
        expand_layout.addWidget(self.expand_btn)
        
        main_layout.addWidget(expand_container)
        main_layout.addStretch()

    def setup_expanded_ui(self, main_layout):
        """Setup UI for expanded state"""
        self.clear_layout(main_layout)
        
        # Settings panel
        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                background: #000000;
                color: #f5e6c0;
                font-weight: bold;
                border: 2px solid #2a2a2a;
                border-radius: 0px;
                margin: 3px 0px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #2a2a2a;
            }
        """)
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(8, 8, 8, 8)
        settings_layout.setSpacing(5)
        
        # External window toggle - restore from config
        self.external_cb = QCheckBox("Open tools externally")
        saved_external = self.config.get("open_external", True)
        self.external_cb.setChecked(saved_external)
        self.external_cb.stateChanged.connect(self.toggle_external_mode)
        self.external_cb.setStyleSheet("""
            QCheckBox {
                color: #f5e6c0;
                spacing: 8px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #4a4a4a;
                border: 2px solid #2a2a2a;
                border-radius: 0px;
            }
            QCheckBox::indicator:checked {
                background-color: #8b4a4a;
                border: 2px solid #2a2a2a;
                border-radius: 0px;
            }
        """)
        settings_layout.addWidget(self.external_cb)
        
        settings_group.setLayout(settings_layout)
        settings_group.setMaximumHeight(70)
        main_layout.addWidget(settings_group)
        
        # IRC Chat toggle button - restore state
        self.chat_toggle_btn = QPushButton("IRC Chat")
        self.chat_toggle_btn.setFixedHeight(35)
        self.chat_toggle_btn.clicked.connect(self.toggle_chat)
        
        # Set button style based on saved chat visibility
        is_visible = self.config.get("chat_panel_visible", True)
        self.update_chat_button_style(is_visible)
        
        main_layout.addWidget(self.chat_toggle_btn)
        
        # Tools panel
        tools_group = QGroupBox("Tools")
        tools_group.setStyleSheet("""
            QGroupBox {
                background: #000000;
                color: #f5e6c0;
                font-weight: bold;
                border: 2px solid #2a2a2a;
                border-radius: 0px;
                margin: 3px 0px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #2a2a2a;
            }
        """)
        tools_layout = QVBoxLayout()
        tools_layout.setContentsMargins(5, 5, 5, 5)
        tools_layout.setSpacing(4)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: #000000;
                border: 1px solid #2a2a2a;
                margin: 0px;
                padding: 0px;
            }
            QScrollArea > QWidget > QWidget {
                background: #000000;
                margin: 0px;
                padding: 0px;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 14px;
                margin: 0px;
                border: 1px solid #2a2a2a;
            }
            QScrollBar::handle:vertical {
                background: #8b4a4a;
                min-height: 20px;
                border-radius: 0px;
                border: 1px solid #2a2a2a;
            }
            QScrollBar::handle:vertical:hover {
                background: #a55a5a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background: #000000; margin: 0px; padding: 0px;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(4)
        self.scroll_layout.setContentsMargins(5, 5, 20, 5)
        
        # Create tool buttons
        self.tool_buttons = []
        tool_urls = get_tool_urls()
        for tool_name, url in tool_urls.items():
            btn = self.create_tool_button(tool_name, url)
            self.scroll_layout.addWidget(btn)
            self.tool_buttons.append(btn)
        
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_widget)
        tools_layout.addWidget(self.scroll_area)
        
        tools_group.setLayout(tools_layout)
        main_layout.addWidget(tools_group, 1)

    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def expand_panel(self):
        """Expand the panel from collapsed state"""
        self.collapsed = False
        set_config_value("right_panel_collapsed", False)
        
        # Set to optimal width for expanded state
        self.setFixedWidth(self.optimal_width)
        
        # Rebuild UI for expanded state
        main_layout = self.layout()
        self.setup_expanded_ui(main_layout)
        
        # Emit signal to parent to handle layout changes
        self.panel_collapse_requested.emit(False)
        
        # Apply fonts after rebuilding UI
        QTimer.singleShot(100, self.force_apply_readable_fonts)

    def set_collapsed_state(self, collapsed):
        """Set collapse state and rebuild UI accordingly"""
        if self.collapsed != collapsed:
            self.collapsed = collapsed
            set_config_value("right_panel_collapsed", collapsed)
            
            # Set appropriate width
            if collapsed:
                self.setFixedWidth(25)
            else:
                self.setFixedWidth(self.optimal_width)
            
            # Rebuild UI based on new state
            main_layout = self.layout()
            if collapsed:
                self.setup_collapsed_ui(main_layout)
            else:
                self.setup_expanded_ui(main_layout)
                # Apply fonts after rebuilding UI
                QTimer.singleShot(100, self.force_apply_readable_fonts)

    def update_chat_button_style(self, is_visible):
        """Update chat button style based on visibility"""
        if self.collapsed:
            return
            
        if is_visible:
            self.chat_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a6a4a;
                    border: 1px solid #2a2a2a;
                    border-radius: 0px;
                    padding: 8px 12px;
                    color: #f5e6c0;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a7a5a;
                    border-color: #4a6a4a;
                }
                QPushButton:pressed {
                    background-color: #4a6a4a;
                    border: 1px inset #2a2a2a;
                }
            """)
        else:
            self.chat_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8b4a4a;
                    border: 1px solid #2a2a2a;
                    border-radius: 0px;
                    padding: 8px 12px;
                    color: #f5e6c0;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #a55a5a;
                    border-color: #8b4a4a;
                }
                QPushButton:pressed {
                    background-color: #8b4a4a;
                    border: 1px inset #2a2a2a;
                }
            """)

    def toggle_chat(self):
        """Emit signal to toggle chat panel"""
        self.chat_toggle_requested.emit()

    def create_tool_button(self, name, url):
        """Create a tool button with optimal sizing"""
        icon_path = get_icon_path(name)
        
        display_name = name
        if len(name) > 12:
            if name == "Clue Coordinates":
                display_name = "Coordinates"
            elif name == "Clue Scroll Help":
                display_name = "Clue Help"
            elif name == "Market Prices":
                display_name = "Prices"
        
        if os.path.exists(icon_path) and icon_path.endswith('.png'):
            btn = QPushButton()
            icon = QIcon(icon_path)
            btn.setIcon(icon)
            btn.setIconSize(QSize(26, 26))
            btn.setText(display_name)
        else:
            btn = QPushButton(f"{icon_path} {display_name}")
        
        btn.setProperty("display_name", display_name)
        btn.setProperty("icon_path", icon_path)
        
        btn.setStyleSheet(self.get_button_style())
        btn.setFixedHeight(42)
        btn.setMinimumWidth(160)
        btn.setMaximumWidth(200)
        
        btn.clicked.connect(lambda checked, n=name, u=url: self.open_tool(n, u))
        return btn

    def get_button_style(self):
        """Get button style optimized for the panel width"""
        button_image_path = "button.jpg"
        base_style = """
            QPushButton {
                border: 2px solid #2a2a2a;
                border-radius: 0px;
                padding: 6px 10px;
                color: #f5e6c0;
                font-weight: bold;
                min-height: 38px;
                max-height: 42px;
                text-align: left;
        """
        
        if os.path.exists(button_image_path):
            base_style += f"background: url({button_image_path}) center center stretch;"
        else:
            base_style += "background-color: #8b4a4a;"
        
        base_style += """
            }
            QPushButton:hover {
                border-color: #8b4a4a;
                background-color: rgba(139, 74, 74, 120);
            }
            QPushButton:pressed {
                border: 2px inset #2a2a2a;
                background-color: rgba(139, 74, 74, 150);
            }
        """
        
        return base_style
        
    def open_tool(self, name, url):
        """Open a tool either in external window or in-game browser"""
        print(f"Opening tool: {name} -> {url}")
        
        max_windows = get_config_value("max_tool_windows", 10)
        
        # Get current external mode setting
        external_mode = get_config_value("open_external", True)
        
        if external_mode:
            self.cleanup_dead_windows()
            
            if len(self.tool_windows) >= max_windows:
                QMessageBox.warning(
                    self, 
                    "Window Limit Reached",
                    f"Maximum number of tool windows ({max_windows}) reached.\nPlease close some windows before opening new ones.",
                    QMessageBox.StandardButton.Ok
                )
                return
            
            window_key = f"{name}_{self.window_count}"
            
            try:
                tool_window = ToolWindow(url, name, self)
                tool_window.show()
                
                self.tool_windows[window_key] = tool_window
                self.window_count += 1
                
                print(f"Opened {name} in external window ({len(self.tool_windows)}/{max_windows})")
                
            except Exception as e:
                print(f"Error creating tool window: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to open {name}:\n{str(e)}",
                    QMessageBox.StandardButton.Ok
                )
        else:
            print(f"Emitting browser_requested signal for {name}")
            self.browser_requested.emit(url, name)

    def cleanup_dead_windows(self):
        """Remove references to closed windows"""
        dead_keys = []
        for key, window_ref in list(self.tool_windows.items()):
            try:
                if not hasattr(window_ref, 'isVisible') or not window_ref.isVisible():
                    dead_keys.append(key)
            except RuntimeError:
                dead_keys.append(key)
        
        for key in dead_keys:
            if key in self.tool_windows:
                del self.tool_windows[key]
        
        if dead_keys:
            print(f"Cleaned up {len(dead_keys)} dead window references")
            
    def toggle_external_mode(self, state):
        """Toggle between external windows and in-game browser"""
        external = state == Qt.CheckState.Checked.value
        set_config_value("open_external", external)
        print(f"External mode set to: {external}")
        
        if not external:
            self.close_all_tool_windows()

    def close_all_tool_windows(self):
        """Close all external tool windows"""
        windows_to_close = []
        
        for window_ref in list(self.tool_windows.values()):
            try:
                if hasattr(window_ref, 'isVisible') and window_ref.isVisible():
                    windows_to_close.append(window_ref)
            except RuntimeError:
                pass
        
        for window in windows_to_close:
            try:
                window.close()
            except RuntimeError:
                pass
        
        self.tool_windows.clear()
        self.window_count = 0
        print("Closed all external tool windows")

    def closeEvent(self, event):
        """Clean up tool windows when panel is closed"""
        self.close_all_tool_windows()
        gc.collect()
        event.accept()
