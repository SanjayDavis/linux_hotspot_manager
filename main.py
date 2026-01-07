#!/usr/bin/env python3
"""
RTL8852BE WiFi Diagnostic and Hotspot Manager

A GTK4/libadwaita application for managing WiFi hotspot functionality
on systems equipped with Realtek RTL8852BE wireless chipsets.
"""

import sys
import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio
from ui_components import DiagnosticsPage, HotspotControlPage


class WiFiHotspotApp(Adw.Application):
    
    def __init__(self):
        super().__init__(
            application_id='com.realtek.wifi.hotspot',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.window = None
        
        # Set default icon for the application
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            Gtk.Window.set_default_icon_name("wifi-hotspot-manager")
    
    def do_activate(self):
        if not self.window:
            self.window = WiFiHotspotWindow(application=self)
        self.window.present()


class WiFiHotspotWindow(Adw.ApplicationWindow):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("WiFi Hotspot Manager")
        self.set_default_size(600, 700)
        self._build_ui()
    
    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        header = Adw.HeaderBar()
        main_box.append(header)
        
        menu_button = Gtk.MenuButton()
        menu = Gio.Menu()
        menu.append("About", "app.about")
        menu.append("Quit", "app.quit")
        menu_button.set_menu_model(menu)
        menu_button.set_icon_name("open-menu-symbolic")
        header.pack_end(menu_button)
        
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.get_application().add_action(about_action)
        
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.get_application().quit())
        self.get_application().add_action(quit_action)
        
        self.toast_overlay = Adw.ToastOverlay()
        main_box.append(self.toast_overlay)
        
        stack = Adw.ViewStack()
        stack.set_vexpand(True)
        
        diagnostics_page = DiagnosticsPage()
        page = stack.add_titled(diagnostics_page, "diagnostics", "Diagnostics")
        page.set_icon_name("preferences-system-symbolic")
        
        hotspot_page = HotspotControlPage(on_toast=self._show_toast)
        page = stack.add_titled(hotspot_page, "hotspot", "Hotspot")
        page.set_icon_name("network-wireless-symbolic")
        
        view_switcher = Adw.ViewSwitcher()
        view_switcher.set_stack(stack)
        view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(view_switcher)
        
        self.toast_overlay.set_child(stack)
        self.set_content(main_box)
    
    def _show_toast(self, message: str):
        if not message:
            return
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)
    
    def _on_about(self, action, param):
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        icon_name = "network-wireless-hotspot"
        if os.path.exists(icon_path):
            icon_name = icon_path
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="WiFi Hotspot Manager",
            application_icon=icon_name,
            developer_name="WiFi Manager Project",
            version="1.0.0",
            developers=["WiFi Manager Contributors"],
            copyright="© 2025 WiFi Manager Project",
            license_type=Gtk.License.MIT_X11,
            comments="Manage WiFi hotspot functionality for Realtek RTL8852BE chipsets"
        )
        about.add_link("GitHub", "https://github.com/yourusername/wifi-hotspot-manager")
        about.present()


def main():
    try:
        app = WiFiHotspotApp()
        return app.run(sys.argv)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
