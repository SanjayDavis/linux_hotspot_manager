"""
System diagnostics module for Realtek RTL8852BE WiFi driver detection.
"""

import subprocess
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class DriverStatus:
    loaded: bool
    version: Optional[str] = None
    firmware_loaded: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class APCapabilities:
    supported: bool
    bands_2ghz: bool = False
    bands_5ghz: bool = False
    max_interfaces: int = 0
    interface_combinations: List[str] = field(default_factory=list)


class SystemDiagnostics:

    @staticmethod
    def check_driver_loaded() -> DriverStatus:
        try:
            result = subprocess.run(
                ['dmesg'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                rtw89_pattern = re.compile(r'rtw89', re.IGNORECASE)
                driver_loaded = bool(rtw89_pattern.search(output))
                
                if not driver_loaded:
                    return SystemDiagnostics._check_via_lsmod()
                
                version_match = re.search(r'rtw89.*?version\s+(\S+)', output, re.IGNORECASE)
                version = version_match.group(1) if version_match else None
                
                firmware_loaded = bool(re.search(r'rtw89.*?firmware.*?(loaded|ready)', output, re.IGNORECASE))
                
                errors = []
                warnings = []
                
                if re.search(r'rtw89.*?firmware.*?fail', output, re.IGNORECASE):
                    errors.append("Firmware load failure detected")
                
                if re.search(r'rtw89.*?ASPM', output, re.IGNORECASE):
                    warnings.append("ASPM-related warning detected")
                
                if re.search(r'rtw89.*?power.*?save.*?(fail|error)', output, re.IGNORECASE):
                    warnings.append("Power save issue detected")
                
                if re.search(r'rtw89.*?timeout', output, re.IGNORECASE):
                    warnings.append("Timeout issue detected")
                
                return DriverStatus(
                    loaded=True,
                    version=version,
                    firmware_loaded=firmware_loaded,
                    errors=errors,
                    warnings=warnings
                )
            else:
                return SystemDiagnostics._check_via_lsmod()
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return SystemDiagnostics._check_via_lsmod()
    
    @staticmethod
    def _check_via_lsmod() -> DriverStatus:
        try:
            result = subprocess.run(
                ['lsmod'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode != 0:
                return DriverStatus(loaded=False, errors=["Cannot check driver status"])
            
            output = result.stdout
            
            if re.search(r'rtw89', output, re.IGNORECASE):
                modules = []
                for line in output.split('\n'):
                    if 'rtw89' in line.lower():
                        parts = line.split()
                        if parts:
                            modules.append(parts[0])
                
                warnings = ["Using lsmod check (dmesg requires root access)"]
                
                return DriverStatus(
                    loaded=True,
                    version=None,
                    firmware_loaded=True,
                    errors=[],
                    warnings=warnings
                )
            else:
                return DriverStatus(loaded=False)
                
        except Exception as e:
            return DriverStatus(loaded=False, errors=[f"Driver check failed: {str(e)}"])

    @staticmethod
    def check_ap_support() -> APCapabilities:
        try:
            result = subprocess.run(
                ['iw', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return APCapabilities(supported=False)
            
            output = result.stdout
            
            ap_supported = bool(re.search(r'\* AP', output, re.MULTILINE))
            
            if not ap_supported:
                return APCapabilities(supported=False)
            
            bands_2ghz = bool(re.search(r'Band \d+:.*?2\d{3} MHz', output, re.DOTALL))
            bands_5ghz = bool(re.search(r'Band \d+:.*?5\d{3} MHz', output, re.DOTALL))
            
            combinations = []
            combination_section = re.search(
                r'valid interface combinations:(.*?)(?=\n\w|\Z)',
                output,
                re.DOTALL
            )
            
            if combination_section:
                combo_text = combination_section.group(1)
                ap_combos = re.findall(r'\* #\{ AP.*?\}', combo_text, re.DOTALL)
                combinations = [combo.strip() for combo in ap_combos]
            
            max_interfaces = 1
            max_match = re.search(r'#\{ AP.*?\} <= (\d+)', output, re.DOTALL)
            if max_match:
                max_interfaces = int(max_match.group(1))
            
            return APCapabilities(
                supported=True,
                bands_2ghz=bands_2ghz,
                bands_5ghz=bands_5ghz,
                max_interfaces=max_interfaces,
                interface_combinations=combinations
            )
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return APCapabilities(supported=False)

    @staticmethod
    def check_permissions() -> Tuple[bool, Optional[str]]:
        try:
            result = subprocess.run(
                ['nmcli', 'general', 'status'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode != 0:
                return False, "NetworkManager not accessible"
            
            return True, None
            
        except FileNotFoundError:
            return False, "NetworkManager (nmcli) not found"
        except Exception as e:
            return False, f"Permission check failed: {str(e)}"

    @staticmethod
    def get_wireless_interfaces() -> List[str]:
        try:
            result = subprocess.run(
                ['iw', 'dev'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode != 0:
                return []
            
            interfaces = re.findall(r'Interface\s+(\S+)', result.stdout)
            return interfaces
            
        except Exception:
            return []
