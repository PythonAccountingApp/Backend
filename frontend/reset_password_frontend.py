import gi
import json
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
import requests


class PasswordResetApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.PasswordReset")
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = PasswordResetRequestWindow(application=self)
        self.window.present()


class PasswordResetRequestWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_title("密碼重置請求")
        self.set_default_size(400, 200)

        # Main Layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        self.set_child(box)

        # Email Input
        self.email_entry = Gtk.Entry()
        self.email_entry.set_placeholder_text("輸入您的電子郵件")
        box.append(self.email_entry)

        # Submit Button
        self.submit_button = Gtk.Button(label="請求重置密碼")
        self.submit_button.connect("clicked", self.on_submit_clicked)
        box.append(self.submit_button)

        # Status Label
        self.status_label = Gtk.Label(label="")
        box.append(self.status_label)

    def on_submit_clicked(self, button):
        email = self.email_entry.get_text()
        if not email:
            self.status_label.set_text("請輸入有效的電子郵件")
            return

        try:
            # 發送密碼重置請求到後端
            response = requests.post(
                "http://localhost:8000/auth/password-reset/",
                json={"email": email}  # 注意正確使用 JSON 格式
            )
            if response.status_code == 200:
                self.status_label.set_text("密碼重置郵件已發送，請檢查您的郵箱")
            else:
                error_message = response.json().get("error", "無法處理請求")
                self.status_label.set_text(f"錯誤：{error_message}")
        except Exception as e:
            self.status_label.set_text(f"請求失敗：{str(e)}")


if __name__ == "__main__":
    app = PasswordResetApp()
    app.run()
