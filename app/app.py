from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    nb_clients = 5
    nb_projets = 3
    nb_intervenants = 8
    return render_template('dashboard.html',
                           nb_clients=nb_clients,
                           nb_projets=nb_projets,
                           nb_intervenants=nb_intervenants)

if __name__ == '__main__':
    app.run(debug=True)
