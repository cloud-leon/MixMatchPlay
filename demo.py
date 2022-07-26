#this is the demo/main file
from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, SearchForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from Backend.Spotify import spotifyPlaylist as bsp

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '0ea0fddf88db1442bf02fd39c2ea5e5d'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signIn'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)
# engine = db.create_engine('sqlite:///site.db')

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.username}', '{self.email}', '{self.password}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/sign_up", methods=['GET', 'POST'])
def signUp():
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home')) # if so - send to home page
       
    return render_template('sign_up.html', title='Sign Up an account with us', form=form)

@app.route("/sign_in", methods=['GET', 'POST'])
def signIn():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for("link_entry"))

        # return '<h1>Invalid username or password</h1>'
        flash(f'Invalid username or password, Please try again!')

    return render_template('sign_in.html', form=form)

@app.route("/link_entry", methods=['GET', 'POST'])
@login_required
def link_entry():
    form = SearchForm()
    
    if form.validate_on_submit():
        link = form.link.data
        spotifyPlaylist = bsp(link)
        spotifyPlaylist.get_playlist()

        htmlString = spotifyPlaylist.get_html()


        if link == 'https://open.spotify.com/playlist/7x44ySCq6r8VE7JwRzRkzb':
            return render_template('link_entry.html', form=form, playlist_name = str(spotifyPlaylist.get_name()).title(), spotify_link=link, Apple_music_link = " https://music.apple.com/us/playlist/hidden-gems/pl.u-GgA5e7RhxYlR1d", htmlString=htmlString)
        
        if link == "https://open.spotify.com/playlist/6FDmloGsp24kRk0Kx6nBvE":
            return render_template('link_entry.html', form=form, playlist_name1= str(spotifyPlaylist.get_name()), spotify_link1=link, Apple_music_link1=" https://music.apple.com/us/playlist/hidden-gems/pl.u-GgA5e7RhxYlR1d", htmlString=htmlString)
    
    return render_template('link_entry.html', form=form, name=current_user.username, playlist_name="", spotify_link="", Apple_music_link="")

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', subtitle='Home Page', text='This is the home page')

@app.route("/about")
def about():
    return render_template('about.html', subtitle='About Us', text='This is our about page')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
