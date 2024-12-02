from PyThreadKiller import PyThreadKiller
import flask
from waitress import serve

class GithubLoginServer:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.serverThread = PyThreadKiller(self.run_server)
        self.callbackData = None

        # 路由註冊
        self.app.add_url_rule("/", "root", self.root)
        self.app.add_url_rule("/github/callback", "hello", self.hello, methods=["GET"])

    def run_server(self):
        serve(self.app, host="localhost", port=53269)

    def root(self):
        return "ss"

    def hello(self):
        from flask import request, render_template
        if request.args.get("code") is not None:
            self.callbackData = request.args.get("code")
            self.serverThread.kill()
            return render_template("login_successful.html")
        else:
            return render_template("login_failure.html")

    def GithubLoginServerStart(self):
        print("Server Start")
        self.serverThread.start()
