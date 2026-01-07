"""
Network control module for WiFi hotspot management.
"""

import subprocess
import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class HotspotStatus:
    active: bool
    ssid: Optional[str] = None
    interface: Optional[str] = None
    band: Optional[str] = None
    password: Optional[str] = None


class NetworkControl:

    @staticmethod
    def get_hotspot_status() -> HotspotStatus:
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,TYPE,DEVICE', 'connection', 'show', '--active'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode != 0:
                return HotspotStatus(active=False)
            
            output = result.stdout
            if not output or not output.strip():
                return HotspotStatus(active=False)
            
            hotspot_name = None
            interface = None
            
            for line in output.strip().split('\n'):
                if not line:
                    continue
                parts = line.split(':')
                if len(parts) >= 3:
                    name, conn_type, device = parts[0], parts[1], parts[2]
                    
                    if '802-11-wireless' in conn_type or 'wifi' in conn_type.lower():
                        detail_result = subprocess.run(
                            ['nmcli', '-t', '-f', '802-11-wireless.mode', 'connection', 'show', name],
                            capture_output=True,
                            text=True,
                            timeout=3
                        )
                        
                        if detail_result.returncode == 0:
                            mode_output = detail_result.stdout.strip()
                            if 'ap' in mode_output.lower():
                                hotspot_name = name
                                interface = device
                                break
            
            if not hotspot_name:
                return HotspotStatus(active=False)
            
            result = subprocess.run(
                ['nmcli', '-t', '-f', '802-11-wireless.ssid,802-11-wireless.band', 'connection', 'show', hotspot_name],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            ssid = None
            band = None
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if 'ssid:' in line.lower():
                        ssid = line.split(':', 1)[1].strip() if ':' in line else None
                    elif 'band:' in line.lower():
                        band_value = line.split(':', 1)[1].strip() if ':' in line else ''
                        if 'bg' in band_value or '2.4' in band_value:
                            band = "2.4GHz"
                        elif 'a' in band_value or '5' in band_value:
                            band = "5GHz"
            
            password = None
            pwd_result = subprocess.run(
                ['nmcli', '-s', '-t', '-f', '802-11-wireless-security.psk', 'connection', 'show', hotspot_name],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if pwd_result.returncode == 0:
                for line in pwd_result.stdout.strip().split('\n'):
                    if 'psk:' in line.lower():
                        password = line.split(':', 1)[1].strip() if ':' in line else None
            
            return HotspotStatus(
                active=True,
                ssid=ssid,
                interface=interface,
                band=band,
                password=password
            )
            
        except Exception:
            return HotspotStatus(active=False)

    @staticmethod
    def enable_hotspot(
        ssid: Optional[str] = None,
        password: Optional[str] = None,
        interface: Optional[str] = None,
        band: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        try:
            cmd = ['nmcli', 'device', 'wifi', 'hotspot']
            
            if interface and interface.strip():
                cmd.extend(['ifname', interface.strip()])
            
            if ssid and ssid.strip():
                cmd.extend(['ssid', ssid.strip()])
            
            if password and password.strip():
                if len(password.strip()) < 8:
                    return False, "Password must be at least 8 characters"
                cmd.extend(['password', password.strip()])
            
            if band and band.strip():
                if band == '2.4':
                    cmd.extend(['band', 'bg'])
                elif band == '5':
                    cmd.extend(['band', 'a'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or "Failed to enable hotspot"
                
                if 'not found' in error_msg.lower():
                    return False, "Network interface not found"
                elif 'permission' in error_msg.lower():
                    return False, "Insufficient permissions - run with sudo or add user to netdev group"
                elif 'already' in error_msg.lower():
                    return False, "Hotspot already active"
                else:
                    return False, error_msg
            
            output = result.stdout
            password_match = re.search(r'password:\s+(\S+)', output)
            generated_password = password_match.group(1) if password_match else None
            
            if generated_password:
                return True, f"Hotspot enabled. Password: {generated_password}"
            
            return True, None
            
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, "nmcli command not found - ensure NetworkManager is installed"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def disable_hotspot() -> Tuple[bool, Optional[str]]:
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split(':')
                    if len(parts) >= 2:
                        name, conn_type = parts[0], parts[1]
                        
                        if '802-11-wireless' in conn_type or 'wifi' in conn_type.lower():
                            detail_result = subprocess.run(
                                ['nmcli', '-t', '-f', '802-11-wireless.mode', 'connection', 'show', name],
                                capture_output=True,
                                text=True,
                                timeout=3
                            )
                            
                            if detail_result.returncode == 0 and 'ap' in detail_result.stdout.lower():
                                result = subprocess.run(
                                    ['nmcli', 'connection', 'down', name],
                                    capture_output=True,
                                    text=True,
                                    timeout=5
                                )
                                
                                if result.returncode != 0:
                                    return False, "Failed to disconnect hotspot"
                                
                                return True, None
            
            return True, None
            
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, "nmcli command not found"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def get_device_status(interface: str) -> Optional[str]:
        if not interface or not interface.strip():
            return None
            
        try:
            result = subprocess.run(
                ['nmcli', 'device', 'status'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode != 0:
                return None
            
            for line in result.stdout.split('\n'):
                if interface in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]
            
            return None
            
        except Exception:
            return None
