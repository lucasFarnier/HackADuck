from flask import Flask, request


PORT = 60000
app = Flask(__name__)

@app.route('/hello', methods=["GET"])
def helloWorld():
    print("/hello has been accessed")
    return "Hello world!", 200



if __name__ == "__main__":
    app.run(port=PORT)