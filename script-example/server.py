from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World! From Solo!"

if __name__ == "__main__":
    app.run('10.1.1.10', 8888)
