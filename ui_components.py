"""
GTK4/libadwaita UI components for WiFi Hotspot Manager.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import Callable, Optional
from diagnostics import SystemDiagnostics, DriverStatus, APCapabilities
from network_control import NetworkControl, HotspotStatus


class DiagnosticsPage(Gtk.Box):
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        title = Gtk.Label(label="System Diagnostics")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        self.append(title)
        
        self.driver_card = self._create_info_card("Driver Status", "Checking...")
        self.append(self.driver_card)
        
        self.ap_card = self._create_info_card("AP Mode Support", "Checking...")
        self.append(self.ap_card)
        
        self.perm_card = self._create_info_card("Permissions", "Checking...")
        self.append(self.perm_card)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(12)
        
        refresh_btn = Gtk.Button(label="Refresh Diagnostics")
        refresh_btn.add_css_class("suggested-action")
        refresh_btn.connect("clicked", lambda _: self.refresh())
        button_box.append(refresh_btn)
        
        self.append(button_box)
        
        GLib.timeout_add(100, self.refresh)
    
    def _create_info_card(self, title: str, content: str) -> Gtk.Frame:
        frame = Gtk.Frame()
        frame.set_margin_top(6)
        frame.set_margin_bottom(6)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("title-4")
        title_label.set_halign(Gtk.Align.START)
        box.append(title_label)
        
        content_label = Gtk.Label(label=content)
        content_label.set_halign(Gtk.Align.START)
        content_label.set_wrap(True)
        content_label.set_xalign(0)
        box.append(content_label)
        
        frame.content_label = content_label
        frame.set_child(box)
        return frame
    
    def refresh(self) -> bool:
        driver_status = SystemDiagnostics.check_driver_loaded()
        self._update_driver_status(driver_status)
        
        ap_caps = SystemDiagnostics.check_ap_support()
        self._update_ap_status(ap_caps)
        
        has_perm, error = SystemDiagnostics.check_permissions()
        self._update_permission_status(has_perm, error)
        
        return False
    
    def _update_driver_status(self, status: DriverStatus):
        if not status.loaded:
            text = "Driver not loaded\n"
            if status.errors:
                text += "\n".join(f"  • {err}" for err in status.errors)
        else:
            text = "rtw89 driver loaded"
            if status.version:
                text += f" (version {status.version})"
            
            if status.firmware_loaded:
                text += "\nFirmware loaded successfully"
            
            if status.warnings:
                text += "\n\nWarnings:"
                text += "\n" + "\n".join(f"  • {warn}" for warn in status.warnings)
            
            if status.errors:
                text += "\n\nErrors:"
                text += "\n" + "\n".join(f"  • {err}" for err in status.errors)
        
        self.driver_card.content_label.set_text(text)
    
    def _update_ap_status(self, caps: APCapabilities):
        if not caps.supported:
            text = "Access Point mode not supported"
        else:
            text = "Access Point mode supported\n"
            
            if caps.bands_2ghz:
                text += "  • 2.4 GHz band available\n"
            if caps.bands_5ghz:
                text += "  • 5 GHz band available\n"
            
            text += f"  • Max interfaces: {caps.max_interfaces}"
        
        self.ap_card.content_label.set_text(text)
    
    def _update_permission_status(self, has_perm: bool, error: Optional[str]):
        if has_perm:
            text = "NetworkManager accessible"
        else:
            text = f"Permission issue\n  • {error or 'Unknown error'}"
        
        self.perm_card.content_label.set_text(text)


class HotspotControlPage(Gtk.Box):
    
    def __init__(self, on_toast: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        self.on_toast = on_toast
        self.updating = False
        
        title = Gtk.Label(label="Hotspot Control")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        self.append(title)
        
        self.status_card = self._create_status_card()
        self.append(self.status_card)
        
        control_card = self._create_control_card()
        self.append(control_card)
        
        GLib.timeout_add(100, self._update_status)
    
    def _create_status_card(self) -> Gtk.Frame:
        frame = Gtk.Frame()
        frame.set_margin_top(6)
        frame.set_margin_bottom(6)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        title_label = Gtk.Label(label="Current Status")
        title_label.add_css_class("title-4")
        title_label.set_halign(Gtk.Align.START)
        box.append(title_label)
        
        self.status_label = Gtk.Label(label="Checking...")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_wrap(True)
        self.status_label.set_xalign(0)
        box.append(self.status_label)
        
        frame.set_child(box)
        return frame
    
    def _create_control_card(self) -> Gtk.Frame:
        frame = Gtk.Frame()
        frame.set_margin_top(6)
        frame.set_margin_bottom(6)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        switch_box.set_halign(Gtk.Align.FILL)
        
        switch_label = Gtk.Label(label="Enable Hotspot")
        switch_label.set_hexpand(True)
        switch_label.set_halign(Gtk.Align.START)
        switch_box.append(switch_label)
        
        self.hotspot_switch = Gtk.Switch()
        self.hotspot_switch.set_valign(Gtk.Align.CENTER)
        self.hotspot_switch.connect("state-set", self._on_switch_toggled)
        switch_box.append(self.hotspot_switch)
        
        box.append(switch_box)
        
        ssid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        ssid_label = Gtk.Label(label="SSID:")
        ssid_label.set_width_chars(10)
        ssid_label.set_halign(Gtk.Align.START)
        ssid_box.append(ssid_label)
        
        self.ssid_entry = Gtk.Entry()
        self.ssid_entry.set_placeholder_text("Optional - auto-generated if empty")
        self.ssid_entry.set_hexpand(True)
        ssid_box.append(self.ssid_entry)
        
        box.append(ssid_box)
        
        pass_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        pass_label = Gtk.Label(label="Password:")
        pass_label.set_width_chars(10)
        pass_label.set_halign(Gtk.Align.START)
        pass_box.append(pass_label)
        
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Optional - auto-generated if empty")
        self.password_entry.set_visibility(False)
        self.password_entry.set_hexpand(True)
        pass_box.append(self.password_entry)
        
        self.password_toggle = Gtk.ToggleButton()
        self.password_toggle.set_icon_name("view-reveal-symbolic")
        self.password_toggle.set_tooltip_text("Show/Hide Password")
        self.password_toggle.connect("toggled", self._on_password_toggle)
        pass_box.append(self.password_toggle)
        
        box.append(pass_box)
        
        # Band selection
        band_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        band_label = Gtk.Label(label="Band:")
        band_label.set_width_chars(10)
        band_label.set_halign(Gtk.Align.START)
        band_box.append(band_label)
        
        self.band_dropdown = Gtk.DropDown()
        band_model = Gtk.StringList()
        band_model.append("Auto (default)")
        band_model.append("2.4 GHz")
        band_model.append("5 GHz")
        self.band_dropdown.set_model(band_model)
        self.band_dropdown.set_selected(0)
        self.band_dropdown.set_hexpand(True)
        band_box.append(self.band_dropdown)
        
        box.append(band_box)
        
        frame.set_child(box)
        return frame
    
    def _update_status(self) -> bool:
        status = NetworkControl.get_hotspot_status()
        
        if status.active:
            text = "Hotspot Active\n"
            if status.ssid:
                text += f"  • SSID: {status.ssid}\n"
            if status.interface:
                text += f"  • Interface: {status.interface}\n"
            if status.band:
                text += f"  • Band: {status.band}"
            
            self.updating = True
            self.hotspot_switch.set_active(True)
            self.updating = False
            
            if status.ssid:
                self.ssid_entry.set_text(status.ssid)
            self.ssid_entry.set_sensitive(False)
            
            if status.password:
                self.password_entry.set_text(status.password)
            else:
                self.password_entry.set_text("********")
            self.password_entry.set_sensitive(False)
            self.password_toggle.set_sensitive(status.password is not None)
            self.band_dropdown.set_sensitive(False)
        else:
            text = "Hotspot Inactive"
            
            self.updating = True
            self.hotspot_switch.set_active(False)
            self.updating = False
            
            self.ssid_entry.set_sensitive(True)
            self.password_entry.set_sensitive(True)
            self.password_toggle.set_sensitive(True)
            self.band_dropdown.set_sensitive(True)
            
            if not self.ssid_entry.get_sensitive():
                self.ssid_entry.set_text("")
            if self.password_entry.get_text() == "********":
                self.password_entry.set_text("")
        
        self.status_label.set_text(text)
        return False
    
    def _on_password_toggle(self, button: Gtk.ToggleButton):
        visible = button.get_active()
        self.password_entry.set_visibility(visible)
        if visible:
            button.set_icon_name("view-conceal-symbolic")
        else:
            button.set_icon_name("view-reveal-symbolic")
    
    def _on_switch_toggled(self, switch: Gtk.Switch, state: bool) -> bool:
        if self.updating:
            return False
        
        if state:
            ssid = self.ssid_entry.get_text().strip() or None
            password = self.password_entry.get_text().strip() or None
            
            # Get selected band
            band_idx = self.band_dropdown.get_selected()
            band = None
            if band_idx == 1:
                band = '2.4'
            elif band_idx == 2:
                band = '5'
            
            success, message = NetworkControl.enable_hotspot(ssid, password, None, band)
            
            if success:
                self.on_toast("Hotspot enabled successfully")
                if message:
                    self.on_toast(message)
                GLib.timeout_add(500, self._update_status)
            else:
                self.on_toast(f"Failed to enable hotspot: {message}")
                self.updating = True
                switch.set_active(False)
                self.updating = False
                return True
        else:
            success, message = NetworkControl.disable_hotspot()
            
            if success:
                self.on_toast("Hotspot disabled")
                GLib.timeout_add(500, self._update_status)
            else:
                self.on_toast(f"Failed to disable hotspot: {message}")
                self.updating = True
                switch.set_active(True)
                self.updating = False
                return True
        
        return False
