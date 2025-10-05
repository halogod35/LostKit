# world_switcher.py - Updated to allow same-world switching when detail mode differs
import os
import json
import urllib.request
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QCheckBox, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPixmap, QPainter
import config
from font_loader import font_loader


class WorldSwitcherWindow(QMainWindow):
    world_selected = pyqtSignal(str, str, bool)  # world_url, world_info, is_high_detail
    
    def __init__(self, current_world_url="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("LostKit - World Switcher")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setWindowFlags(Qt.WindowType.Window)
        
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        
        # Set black background
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        
        self.current_world_url = current_world_url
        
        # Load world data from remote URL
        self.worlds_data = self.load_worlds_data()
        
        # Detect current detail mode from URL or load from config
        self.is_high_detail = self.detect_detail_mode(current_world_url)
        if self.is_high_detail is None:
            self.is_high_detail = config.get_config_value("world_detail_high", True)
        
        # Load window geometry
        self.load_window_geometry()
        self.setMinimumSize(500, 400)
        
        self.setup_ui()
        QTimer.singleShot(100, self.force_apply_fonts)
    
    def load_worlds_data(self):
        """Load world data from remote URL"""
        worlds_data = []
        try:
            # Fetch world data from remote URL
            remote_url = "https://2004.losthq.rs/pages/api/worlds.php"
            print(f"Fetching world data from: {remote_url}")
            
            with urllib.request.urlopen(remote_url, timeout=10) as response:
                data = response.read().decode('utf-8')
                worlds_data = json.loads(data)
                
            print(f"Loaded {len(worlds_data)} worlds from remote API")
            
        except Exception as e:
            print(f"Error loading world data from remote URL: {e}")
            # No fallback data - return empty list if fetch fails
            worlds_data = []
        
        # Ensure all worlds have both hd and ld URLs
        for world in worlds_data:
            if 'hd' not in world:
                world['hd'] = f"https://w{world['world']}-2004.lostcity.rs/rs2.cgi?plugin=0&world={world['world']}&lowmem=0"
            if 'ld' not in world:
                world['ld'] = f"https://w{world['world']}-2004.lostcity.rs/rs2.cgi?plugin=0&world={world['world']}&lowmem=1"
        
        return worlds_data
    
    def detect_detail_mode(self, url):
        """Detect if URL is high or low detail. Returns True for high, False for low, None if unknown"""
        if not url:
            return None
        
        url_lower = url.lower()
        if 'detail=high' in url_lower or 'lowmem=0' in url_lower:
            return True
        elif 'detail=low' in url_lower or 'lowmem=1' in url_lower:
            return False
        
        return None
    
    def force_apply_fonts(self):
        """Apply readable fonts to world switcher - 1.7x larger"""
        font = QFont()
        if font_loader.is_custom_font_available():
            font.setFamily(font_loader.get_font_family_name())
        else:
            test_font = QFont("Runescape-Quill-Caps", 20)
            if test_font.exactMatch():
                font.setFamily("Runescape-Quill-Caps")
            else:
                font.setFamily("Arial")
        
        font.setPointSize(20)
        font.setWeight(QFont.Weight.Normal)
        self.setFont(font)
    
    def setup_ui(self):
        """Setup the UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with title
        title_label = QLabel("Select World")
        title_label.setStyleSheet("""
            QLabel {
                color: #f5e6c0;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)
        
        # Top row with detail mode and refresh button
        top_row_layout = QHBoxLayout()
        
        # Detail mode section
        detail_layout = QHBoxLayout()
        
        detail_label = QLabel("Graphics Mode:")
        detail_label.setStyleSheet("QLabel { color: #f5e6c0; font-size: 20px; font-weight: bold; }")
        detail_layout.addWidget(detail_label)
        
        self.detail_checkbox = QCheckBox("High Detail")
        self.detail_checkbox.setChecked(self.is_high_detail)
        self.detail_checkbox.setStyleSheet("""
            QCheckBox {
                color: #f5e6c0;
                spacing: 8px;
                background: transparent;
                font-size: 20px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
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
        self.detail_checkbox.stateChanged.connect(self.on_detail_mode_changed)
        detail_layout.addWidget(self.detail_checkbox)
        
        top_row_layout.addLayout(detail_layout)
        
        # Add stretch to push refresh button to the right
        top_row_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedSize(120, 40)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b4a4a;
                border: 2px solid #2a2a2a;
                border-radius: 0px;
                padding: 8px;
                color: #f5e6c0;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #a55a5a;
                border-color: #8b4a4a;
            }
            QPushButton:pressed {
                background-color: #8b4a4a;
                border: 2px inset #2a2a2a;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_world_data)
        top_row_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(top_row_layout)
        
        # Warning toggle checkbox
        self.warning_checkbox = QCheckBox("Show warning when switching worlds")
        self.warning_checkbox.setChecked(config.get_config_value("world_switch_warning", True))
        self.warning_checkbox.setStyleSheet("""
            QCheckBox {
                color: #f5e6c0;
                spacing: 8px;
                background: transparent;
                font-size: 18px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
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
        self.warning_checkbox.stateChanged.connect(self.on_warning_toggle_changed)
        layout.addWidget(self.warning_checkbox)
        
        # Scroll area for worlds
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: #000000;
                border: 2px solid #2a2a2a;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 14px;
                border: 1px solid #2a2a2a;
            }
            QScrollBar::handle:vertical {
                background: #8b4a4a;
                min-height: 20px;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a55a5a;
            }
        """)
        
        self.worlds_widget = QWidget()
        self.worlds_layout = QVBoxLayout(self.worlds_widget)
        self.worlds_layout.setSpacing(5)
        self.worlds_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area.setWidget(self.worlds_widget)
        layout.addWidget(scroll_area)
        
        # Display worlds
        self.display_worlds()
    
    def on_warning_toggle_changed(self, state):
        """Handle warning toggle checkbox change"""
        show_warning = (state == Qt.CheckState.Checked.value)
        config.set_config_value("world_switch_warning", show_warning)
    
    def refresh_world_data(self):
        """Reload world data from remote URL and update the display"""
        print("Refreshing world data from remote URL...")
        
        # Store current world and detail mode to maintain selection
        current_world = self.extract_world_from_url(self.current_world_url)
        current_detail = self.detect_detail_mode(self.current_world_url)
        
        # Reload world data from remote
        self.worlds_data = self.load_worlds_data()
        
        # Refresh display
        self.display_worlds()
        
        # Show feedback
        self.refresh_btn.setText("Refreshed!")
        QTimer.singleShot(1000, lambda: self.refresh_btn.setText("Refresh"))
        
        print(f"World data refreshed - {len(self.worlds_data)} worlds loaded from remote")
    
    def on_detail_mode_changed(self, state):
        """Handle detail mode checkbox change"""
        self.is_high_detail = (state == Qt.CheckState.Checked.value)
        config.set_config_value("world_detail_high", self.is_high_detail)
        
        mode_text = "High Detail" if self.is_high_detail else "Low Detail"
        print(f"Graphics mode changed to: {mode_text}")
        
        # Refresh display to update buttons
        self.display_worlds()
    
    def build_world_url(self, world_data, is_high_detail):
        """Build the complete world URL based on detail mode and world data"""
        if is_high_detail:
            return world_data.get("hd", f"https://w{world_data['world']}-2004.lostcity.rs/rs2.cgi?plugin=0&world={world_data['world']}&lowmem=0")
        else:
            return world_data.get("ld", f"https://w{world_data['world']}-2004.lostcity.rs/rs2.cgi?plugin=0&world={world_data['world']}&lowmem=1")
    
    def load_svg_icon(self, svg_filename, width=32, height=20):
        """Load and render SVG icon to QIcon with flag proportions"""
        svg_path = os.path.join("icons", svg_filename)
        if os.path.exists(svg_path):
            try:
                renderer = QSvgRenderer(svg_path)
                pixmap = QPixmap(width, height)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                return QIcon(pixmap)
            except Exception as e:
                print(f"Error loading SVG {svg_filename}: {e}")
        return None
    
    def get_flag_filename(self, location):
        """Get flag filename based on location"""
        flag_map = {
            "US (Central)": "us.svg",
            "US (West)": "us.svg",
            "US (East)": "us.svg",
            "Finland": "fin.svg",
            "Australia": "aus.svg",
            "Japan": "jp.svg",
            "Singapore": "sg.svg",
        }
        return flag_map.get(location, "us.svg")
    
    def display_worlds(self):
        """Display the worlds in the UI based on current detail mode toggle"""
        # Clear existing widgets
        while self.worlds_layout.count():
            child = self.worlds_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Extract current world number
        current_world = self.extract_world_from_url(self.current_world_url)
        current_detail = self.detect_detail_mode(self.current_world_url)
        
        # Create buttons based on toggle state and loaded world data
        for world_data in self.worlds_data:
            world_num = world_data["world"]
            location = world_data["location"]
            player_count = world_data.get("count", 0)
            flag_svg = self.get_flag_filename(location)
            
            world_btn = self.create_world_button(
                world_data, flag_svg, self.is_high_detail,
                is_current=(str(world_num) == current_world and current_detail == self.is_high_detail)
            )
            self.worlds_layout.addWidget(world_btn)
        
        self.worlds_layout.addStretch()
    
    def create_world_button(self, world_data, flag_svg, is_high_detail, is_current=False):
        """Create a button for a world with button.jpg background and player count"""
        btn = QPushButton()
        btn.setFixedHeight(45)
        
        # Load country flag icon with flag proportions (wider than tall)
        if flag_svg:
            icon = self.load_svg_icon(flag_svg, 32, 20)
            if icon:
                btn.setIcon(icon)
                btn.setIconSize(QSize(32, 20))
        
        # Create button text with player count
        world_num = world_data["world"]
        location = world_data["location"]
        player_count = world_data.get("count", 0)
        detail_text = "HD" if is_high_detail else "LD"
        
        # Format button text with player count
        btn_text = f"World {world_num} - {player_count} players - {location} ({detail_text})"
        btn.setText(btn_text)
        
        # Check if button.jpg exists
        button_image_path = "button.jpg"
        
        # Style based on whether it's the current world
        if is_current:
            if os.path.exists(button_image_path):
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: url({button_image_path}) center center stretch;
                        background-color: rgba(74, 106, 74, 180);
                        border: 2px solid #2a2a2a;
                        border-radius: 0px;
                        padding: 8px;
                        color: #f5e6c0;
                        font-weight: bold;
                        font-size: 20px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(90, 122, 90, 200);
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4a6a4a;
                        border: 2px solid #2a2a2a;
                        border-radius: 0px;
                        padding: 8px;
                        color: #f5e6c0;
                        font-weight: bold;
                        font-size: 20px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #5a7a5a;
                    }
                """)
        else:
            if os.path.exists(button_image_path):
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: url({button_image_path}) center center stretch;
                        border: 2px solid #2a2a2a;
                        border-radius: 0px;
                        padding: 8px;
                        color: #f5e6c0;
                        font-weight: bold;
                        font-size: 20px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(139, 74, 74, 120);
                        border-color: #8b4a4a;
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #8b4a4a;
                        border: 2px solid #2a2a2a;
                        border-radius: 0px;
                        padding: 8px;
                        color: #f5e6c0;
                        font-weight: bold;
                        font-size: 20px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #a55a5a;
                        border-color: #8b4a4a;
                    }
                """)
        
        # Connect click handler
        btn.clicked.connect(lambda: self.on_world_clicked(world_data, is_high_detail))
        
        return btn
    
    def on_world_clicked(self, world_data, is_high_detail):
        """Handle world button click with optional warning"""
        # Extract current world and detail mode
        current_world = self.extract_world_from_url(self.current_world_url)
        current_detail = self.detect_detail_mode(self.current_world_url)
        clicked_world = str(world_data["world"])
        
        # Check if user is clicking the EXACT same world and detail mode
        if clicked_world == current_world and is_high_detail == current_detail:
            # Same world AND same detail mode - do nothing
            return
        
        # Check if warning is enabled AND we are currently in a world (current_world is not None)
        show_warning = config.get_config_value("world_switch_warning", True)
        
        if show_warning and current_world is not None:
            # Show warning dialog only if we're currently in a world
            reply = QMessageBox.warning(
                self,
                "Switch World Warning",
                "Make sure you are logged out before switching world!\n\n"
                "Switching worlds while logged in may cause issues with your game session.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            
            if reply != QMessageBox.StandardButton.Ok:
                # User cancelled the world switch
                return
        
        # Proceed with world switch (either different world OR same world with different detail)
        self.perform_world_switch(world_data, is_high_detail)
    
    def perform_world_switch(self, world_data, is_high_detail):
        """Actually perform the world switch (separated for clarity)"""
        world_url = self.build_world_url(world_data, is_high_detail)
        world_num = world_data["world"]
        location = world_data["location"]
        detail_mode = "HD" if is_high_detail else "LD"
        
        # Create world info for the widget (without player count)
        world_info = f"W{world_num} {location} ({detail_mode})"
        
        self.world_selected.emit(world_url, world_info, is_high_detail)
        self.current_world_url = world_url
        self.is_high_detail = is_high_detail
        
        # Save preference
        config.set_config_value("world_detail_high", is_high_detail)
        
        print(f"Selected: {world_info}")
        print(f"URL: {world_url}")
        
        # Refresh display to update current world highlighting
        self.display_worlds()
    
    def extract_world_from_url(self, url):
        """Extract world number from URL"""
        if not url:
            return None
        
        import re
        match = re.search(r'world[=:](\d+)', url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def update_current_world(self, world_url):
        """Update the currently selected world and detect its detail mode"""
        self.current_world_url = world_url
        
        # Auto-detect detail mode from new URL
        detected_detail = self.detect_detail_mode(world_url)
        if detected_detail is not None:
            self.is_high_detail = detected_detail
            self.detail_checkbox.setChecked(self.is_high_detail)
            config.set_config_value("world_detail_high", self.is_high_detail)
        
        self.display_worlds()
    
    def load_window_geometry(self):
        """Load window geometry from config"""
        try:
            geom = config.get_config_value("world_switcher_geometry", None)
            if geom and isinstance(geom, list) and len(geom) == 4:
                x, y, w, h = [int(val) for val in geom]
                x = max(0, min(x, 1920 - w))
                y = max(0, min(y, 1080 - h))
                w = max(500, min(w, 1920))
                h = max(400, min(h, 1080))
                self.setGeometry(x, y, w, h)
            else:
                self.setGeometry(250, 250, 600, 500)
        except Exception as e:
            print(f"Error loading world switcher geometry: {e}")
            self.setGeometry(250, 250, 600, 500)
    
    def save_window_geometry(self):
        """Save window geometry to config"""
        try:
            geom = self.geometry()
            config.set_config_value("world_switcher_geometry", 
                                   [geom.x(), geom.y(), geom.width(), geom.height()])
        except Exception as e:
            print(f"Error saving world switcher geometry: {e}")
    
    def closeEvent(self, event):
        """Save geometry and settings when closing"""
        self.save_window_geometry()
        config.set_config_value("world_detail_high", self.is_high_detail)
        event.accept()
    
    def resizeEvent(self, event):
        """Handle resize with debounced saving"""
        super().resizeEvent(event)
        if not hasattr(self, 'save_timer'):
            self.save_timer = QTimer(self)
            self.save_timer.setSingleShot(True)
            self.save_timer.timeout.connect(self.save_window_geometry)
        self.save_timer.start(1000)
    
    def moveEvent(self, event):
        """Handle move with debounced saving"""
        super().moveEvent(event)
        if not hasattr(self, 'save_timer'):
            self.save_timer = QTimer(self)
            self.save_timer.setSingleShot(True)
            self.save_timer.timeout.connect(self.save_window_geometry)
        self.save_timer.start(1000)