from wakeonlan import send_magic_packet
import pyautogui


class Device:
    def __init__(self, mac_address: str, ip_address=None):
        self.mac_address = mac_address
        self.ip_address = ip_address

    def start_device(self) -> bool():
        send_magic_packet(self.mac_address)
        return True

    def move_mouse(self) -> bool():
        pyautogui.move(1, 1, duration=.1)
        return True
