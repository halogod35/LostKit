# chat_panel.py
import gc
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
import config


class ChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set font matching the application theme
        font = QFont("RuneScape UF", 13)
        if not font.exactMatch():
            font = QFont("runescape_uf", 13)
        self.setFont(font)
        
        # Set black background
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        
        # Load chat zoom factor from config
        self.chat_zoom_factor = config.get_config_value("chat_zoom_factor", 0.8)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the chat panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Chat title label - 1.5x larger text while keeping same title bar height
        title_label = QLabel("IRC Chat")
        title_label.setStyleSheet("""
            QLabel {
                color: #f5e6c0;
                font-weight: bold;
                font-size: 24px;
                background-color: #2a2a2a;
                border: 2px solid #2a2a2a;
                padding: 2px 10px;
                border-radius: 0px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(22)  # Keep same height
        layout.addWidget(title_label)
        
        # Web view for IRC chat
        self.create_chat_browser()
        layout.addWidget(self.chat_browser)
        
        # Set minimum height for the chat panel
        self.setMinimumHeight(150)
        
        # Apply styling to the panel
        self.setStyleSheet("""
            ChatPanel {
                background-color: #000000;
                border: 2px solid #2a2a2a;
                border-radius: 0px;
            }
        """)
        
    def create_chat_browser(self):
        """Create the web browser for IRC chat with persistent storage"""
        try:
            # Use persistent profile name (no process ID or timestamp)
            profile_name = "ChatPanel"
            
            profile = QWebEngineProfile(profile_name, self)
            
            # Use persistent storage paths that survive restarts
            cache_path = config.get_persistent_cache_path("chat")
            storage_path = config.get_persistent_profile_path("chat")
            
            print(f"Chat using persistent cache: {cache_path}")
            print(f"Chat using persistent storage: {storage_path}")
                
            profile.setCachePath(cache_path)
            profile.setPersistentStoragePath(storage_path)
            
            # Force persistent cookies for login state
            profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            
            # Optimize settings for chat while preserving login functionality
            settings = profile.settings()
            if config.get_config_value("resource_optimization", True):
                settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            
            # Create page and web view
            page = QWebEnginePage(profile, self)
            self.chat_browser = QWebEngineView()
            self.chat_browser.setPage(page)
            
            # Store paths for reference (don't delete persistent data)
            self.cache_path = cache_path
            self.storage_path = storage_path
            
            # Set zoom factor from config
            self.chat_browser.setZoomFactor(self.chat_zoom_factor)
            
            # Style the web view
            self.chat_browser.setStyleSheet("""
                QWebEngineView {
                    background-color: #000000;
                    border: 2px solid #2a2a2a;
                    border-radius: 0px;
                }
            """)
            
            # Load the chat URL
            placeholder_url = "https://irc.losthq.rs"
            print(f"Loading chat URL: {placeholder_url}")
            self.chat_browser.setUrl(QUrl(placeholder_url))
            
            # Connect signals
            self.chat_browser.loadFinished.connect(self.on_chat_load_finished)
            
            # Enable mouse wheel zoom control
            self.chat_browser.wheelEvent = self.chat_wheel_event
            
            # Setup light cleanup timer (preserve login data)
            self.cleanup_timer = QTimer(self)
            self.cleanup_timer.timeout.connect(self.perform_cleanup)
            cleanup_interval = config.get_config_value("cache_cleanup_interval", 300) * 1000
            self.cleanup_timer.start(cleanup_interval)
            
        except Exception as e:
            print(f"Error creating chat browser: {e}")
            # Create a fallback label if web view fails
            self.chat_browser = QLabel("Chat will be available soon!")
            self.chat_browser.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.chat_browser.setStyleSheet("""
                QLabel {
                    color: #f5e6c0;
                    background-color: #2a2a2a;
                    border: 2px solid #2a2a2a;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
            self.cache_path = None
            self.storage_path = None

    def perform_cleanup(self):
        """Perform light cleanup - preserve login data"""
        try:
            if config.get_config_value("resource_optimization", True):
                # Only memory cleanup, don't touch persistent storage
                gc.collect()
        except Exception as e:
            print(f"Error during chat cleanup: {e}")
    
    def chat_wheel_event(self, event):
        """Handle mouse wheel events for chat zoom control"""
        try:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                # Ctrl + wheel = zoom
                delta = event.angleDelta().y()
                zoom_step = 0.1
                
                if delta > 0:
                    self.chat_zoom_factor += zoom_step
                else:
                    self.chat_zoom_factor -= zoom_step
                    
                # Clamp zoom factor to reasonable bounds
                self.chat_zoom_factor = max(0.25, min(self.chat_zoom_factor, 3.0))
                
                # Apply zoom
                self.chat_browser.setZoomFactor(self.chat_zoom_factor)
                
                # Save to config immediately
                config.set_config_value("chat_zoom_factor", self.chat_zoom_factor)
                print(f"Chat zoom set to: {int(self.chat_zoom_factor * 100)}%")
                
                event.accept()
            else:
                # Normal scrolling
                QWebEngineView.wheelEvent(self.chat_browser, event)
        except Exception as e:
            print(f"Error in chat wheelEvent: {e}")
            QWebEngineView.wheelEvent(self.chat_browser, event)
    
    def on_chat_load_finished(self, ok: bool):
        """Handle chat page load completion"""
        if ok:
            print("✅ Chat panel loaded successfully with persistent storage")
            try:
                # Apply saved zoom factor after page loads
                self.chat_browser.setZoomFactor(self.chat_zoom_factor)
                print(f"Applied chat zoom: {int(self.chat_zoom_factor * 100)}%")
            except Exception as e:
                print(f"Error setting chat zoom factor: {e}")
        else:
            print("❌ Failed to load chat panel")
    
    def load_chat_url(self, url):
        """Load a new URL in the chat browser"""
        if hasattr(self.chat_browser, 'setUrl'):
            print(f"Loading new chat URL: {url}")
            self.chat_browser.setUrl(QUrl(url))
        else:
            print("Chat browser not available for URL loading")
    
    def reload_chat(self):
        """Reload the chat browser"""
        if hasattr(self.chat_browser, 'reload'):
            print("Reloading chat browser")
            self.chat_browser.reload()
        else:
            print("Chat browser not available for reloading")

    def cleanup_cache_files(self):
        """Light cleanup - preserve persistent login data and settings"""
        print("Chat panel cleanup: Preserving login data and chat settings")
        # Don't delete persistent storage directories - they contain login sessions
        # and chat preferences that should survive between program restarts

    def reset_chat_settings(self):
        """Completely reset all chat settings (use with caution)"""
        try:
            if self.storage_path and os.path.exists(self.storage_path):
                import shutil
                shutil.rmtree(self.storage_path, ignore_errors=True)
                print(f"RESET: Cleared all chat storage: {self.storage_path}")
                
                # Recreate the directory
                os.makedirs(self.storage_path, exist_ok=True)
                print("Chat settings have been reset - all persistent data cleared")
                
                # Reload the chat to apply the reset
                self.reload_chat()
        except Exception as e:
            print(f"Error resetting chat settings: {e}")

    def closeEvent(self, event):
        """Clean up when chat panel is closed (preserve persistent settings)"""
        # Stop cleanup timer
        if hasattr(self, 'cleanup_timer'):
            self.cleanup_timer.stop()
        
        # Save final chat zoom factor
        try:
            config.set_config_value("chat_zoom_factor", self.chat_zoom_factor)
            print(f"Saved chat zoom factor: {self.chat_zoom_factor}")
        except Exception as e:
            print(f"Error saving chat zoom factor: {e}")
            
        # Clean up web view properly but preserve persistent storage
        if hasattr(self, 'chat_browser') and self.chat_browser:
            try:
                self.chat_browser.setPage(None)
                self.chat_browser.deleteLater()
            except Exception as e:
                print(f"Error cleaning up chat browser: {e}")
        
        # Don't clean persistent storage - it contains login data and settings
        print("Chat panel closed - login data and settings preserved")
        
        gc.collect()
        super().closeEvent(event)
