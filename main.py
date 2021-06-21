from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from forms import RateMovieForm, AddMovieForm
import requests
import os

api_key = os.environ['MOVIE_API_KEY']
movie_search_url = "https://api.themoviedb.org/3/search/movie?"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(movies)):
        movies[i].ranking = len(movies) - i
    db.session.commit()
    return render_template("index.html", movies=movies)


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    movie = Movie.query.get_or_404(id)
    form = RateMovieForm()
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form)

@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        params = {
            "api_key": api_key,
            "query": form.title.data
        }
        response = requests.get(url=movie_search_url, params=params)
        data = response.json()["results"]
        return render_template('select.html', options=data)
    return render_template('add.html', form=form)

@app.route("/find/<int:id>", methods=['GET', 'POST'])
def find(id):
    response = requests.get(url=f"https://api.themoviedb.org/3/movie/{id}?", params={"api_key": api_key})
    data = response.json()
    new_movie = Movie(
        title = data["title"],
        year = data["release_date"].split("-")[0],
        img_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
        description = data["overview"]
    )
    db.session.add(new_movie)
    db.session.commit()
    movies = Movie.query.all()
    movie = movies[-1]
    return redirect(url_for("edit", id=movie.id))

if __name__ == '__main__':
    app.run(debug=True)
