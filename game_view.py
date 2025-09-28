# game_view.py - Fixed syntax error on line 199
import gc
import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl, QDir, pyqtSignal, QTimer
import config


class GameViewWidget(QWebEngineView):
    zoom_changed = pyqtSignal(float)
    
    def __init__(self, url, parent=None):
        super().__init__(parent)

        try:
            # Use persistent profile that survives application restarts
            profile_name = "LostCityGame"  # Fixed name, no process ID
            
            profile = QWebEngineProfile(profile_name, self)
            
            # Use persistent directories that survive application restarts
            cache_path = config.get_persistent_cache_path("game_cache")
            storage_path = config.get_persistent_profile_path("game_profile")
            
            print(f"Game using persistent cache: {cache_path}")
            print(f"Game using persistent storage: {storage_path}")
            
            profile.setCachePath(cache_path)
            profile.setPersistentStoragePath(storage_path)
            
            # Force persistent cookies
            profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            
            # Performance optimizations but keep all login-related features
            settings = profile.settings()
            
            # Enable hardware acceleration and GPU features for game
            settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
            
            # Essential features for game and login functionality
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, True)
            
            # Disable only non-essential features
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)
            if config.get_config_value("resource_optimization", True):
                settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)

            page = QWebEnginePage(profile, self)
            self.setPage(page)
            
            # Store paths for cleanup (but don't delete persistent data)
            self.cache_path = cache_path
            self.storage_path = storage_path

            # Load the game
            self.setUrl(QUrl(url))

            # Load zoom factor from config
            self.zoom_factor = config.get_config_value("zoom_factor", 1.0)
            self.setZoomFactor(self.zoom_factor)

            # Connect signals
            self.page().loadFinished.connect(self.on_load_finished)
            
            # Enable focus for keyboard events
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            # Setup cleanup timer (but preserve persistent data)
            self.cleanup_timer = QTimer(self)
            self.cleanup_timer.timeout.connect(self.perform_cleanup)
            cleanup_interval = config.get_config_value("cache_cleanup_interval", 300) * 1000
            self.cleanup_timer.start(cleanup_interval)
            
        except Exception as e:
            print(f"Error initializing GameViewWidget: {e}")
            self.zoom_factor = 1.0
            self.cache_path = None
            self.storage_path = None

    def perform_cleanup(self):
        """Perform light cleanup without removing persistent data"""
        try:
            if config.get_config_value("resource_optimization", True):
                # Only do memory cleanup, don't touch persistent storage
                gc.collect()
                print("Performed light game view cleanup (preserved login data)")
        except Exception as e:
            print(f"Error during game view cleanup: {e}")

    def on_load_finished(self, ok: bool):
        """Handle page load completion"""
        if ok:
            print("✅ Game page loaded successfully with persistent storage.")
            try:
                self.setZoomFactor(self.zoom_factor)
            except Exception as e:
                print(f"Error setting zoom factor: {e}")
        else:
            print("❌ Failed to load game page.")

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        try:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                delta = event.angleDelta().y()
                zoom_step = 0.1
                
                if delta > 0:
                    self.zoom_factor += zoom_step
                else:
                    self.zoom_factor -= zoom_step
                    
                # Clamp zoom factor
                self.zoom_factor = max(0.25, min(self.zoom_factor, 5.0))
                
                # Apply and save zoom
                self.setZoomFactor(self.zoom_factor)
                config.set_config_value("zoom_factor", self.zoom_factor)
                self.zoom_changed.emit(self.zoom_factor)
                
                event.accept()
            else:
                super().wheelEvent(event)
        except Exception as e:
            print(f"Error in wheelEvent: {e}")
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        try:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_0:
                    # Ctrl+0: Reset zoom to 100%
                    self.zoom_factor = 1.0
                    self.setZoomFactor(self.zoom_factor)
                    config.set_config_value("zoom_factor", self.zoom_factor)
                    self.zoom_changed.emit(self.zoom_factor)
                    event.accept()
                    return
                elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                    # Ctrl++: Zoom in
                    self.zoom_factor = min(self.zoom_factor + 0.1, 5.0)
                    self.setZoomFactor(self.zoom_factor)
                    config.set_config_value("zoom_factor", self.zoom_factor)
                    self.zoom_changed.emit(self.zoom_factor)
                    event.accept()
                    return
                elif event.key() == Qt.Key.Key_Minus:
                    # Ctrl+-: Zoom out
                    self.zoom_factor = max(self.zoom_factor - 0.1, 0.25)
                    self.setZoomFactor(self.zoom_factor)
                    config.set_config_value("zoom_factor", self.zoom_factor)
                    self.zoom_changed.emit(self.zoom_factor)
                    event.accept()
                    return
            
            super().keyPressEvent(event)
        except Exception as e:
            print(f"Error in keyPressEvent: {e}")
            super().keyPressEvent(event)

    def reset_zoom(self):
        """Reset zoom to 100%"""
        try:
            self.zoom_factor = 1.0
            self.setZoomFactor(self.zoom_factor)
            config.set_config_value("zoom_factor", self.zoom_factor)
            self.zoom_changed.emit(self.zoom_factor)
        except Exception as e:
            print(f"Error resetting zoom: {e}")

    def zoom_in(self):
        """Zoom in by one step"""
        try:
            self.zoom_factor = min(self.zoom_factor + 0.1, 5.0)
            self.setZoomFactor(self.zoom_factor)
            config.set_config_value("zoom_factor", self.zoom_factor)
            self.zoom_changed.emit(self.zoom_factor)
        except Exception as e:
            print(f"Error zooming in: {e}")

    def zoom_out(self):
        """Zoom out by one step"""
        try:
            self.zoom_factor = max(self.zoom_factor - 0.1, 0.25)
            self.setZoomFactor(self.zoom_factor)
            config.set_config_value("zoom_factor", self.zoom_factor)
            self.zoom_changed.emit(self.zoom_factor)
        except Exception as e:  # FIXED: Added 'as e' here
            print(f"Error zooming out: {e}")

    def get_zoom_percentage(self):
        """Get current zoom as percentage string"""
        try:
            return f"{int(self.zoom_factor * 100)}%"
        except Exception:
            return "100%"

    def cleanup_cache_files(self):
        """Light cleanup - preserve persistent login data"""
        print("Game view cleanup: Preserving login data and cookies")
        # Don't delete persistent storage directories
        # They contain login sessions and should survive restarts

    def closeEvent(self, event):
        """Clean up when widget is closed - preserve login data"""
        if hasattr(self, 'cleanup_timer'):
            self.cleanup_timer.stop()
            
        # Don't clear persistent storage - just clean up memory
        gc.collect()
        print("Game view closed - login data preserved")
        
        super().closeEvent(event)
