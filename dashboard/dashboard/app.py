from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('coming-soon.html')

if __name__ == '__main__':
    app.run(debug=True)