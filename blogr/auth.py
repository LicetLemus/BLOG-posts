from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    session,
    g,
)

from werkzeug.security import generate_password_hash, check_password_hash

from blogr.models import User
from blogr import db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User(
            username, email, generate_password_hash(password, method="pbkdf2:sha256")
        )

        # validar datos
        error = None

        user_email = User.query.filter_by(email=email).first()
        if user_email == None:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))

        else:
            error = f"El email {email} ya está registrado"

        flash(error, "error")
    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # validar datos
        error = None

        user = User.query.filter_by(email=email).first()

        if user == None or not check_password_hash(user.password, password):
            error = "Email o contraseña incorrectos"

        # iniciar sesion
        if error == None:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("post.posts"))

        flash(error, "error")

    return render_template("auth/login.html")


# mantener logeado un usuario e iniciar sesion
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)


# cerrar sesion
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home.index"))


# login_required

import functools


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view

#editar perfil 

from werkzeug.utils import secure_filename

def get_photo(id):
    user = User.query.get_or_404(id)
    photo = None
    
    if photo != None:
        photo = user.photo
    
    return photo


# pagina del perfil
@bp.route("/profile/<int:id>", methods=["GET", "POST"])
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    
    photo = get_photo(id)

    if request.method == "POST":
        user.username = request.form.get("username")
        password = request.form.get("password")

        error = None
        if password:
            if len(password) < 6:
                error = "Contraseña debe tener al menos 6 caracteres"
                flash(error, "error")  # Agregar la categoría de error
            else:
                user.password = generate_password_hash(password, method="pbkdf2:sha256")

        if request.files['photo']:
            photo = request.files['photo']
            photo.save(f'blogr/static/media/{secure_filename(photo.filename)}')
            user.photo = f'media/{secure_filename(photo.filename)}'

        if error:
            # Si hay un error, no se realiza el commit ni se redirige
            return render_template("auth/profile.html", user=user)

        # Si no hay error, se realiza el commit y se redirige
        db.session.commit()
        flash("Se ha actualizado el perfil", "success")
        return redirect(url_for("auth.profile", id=user.id))

    return render_template("auth/profile.html", user=user, photo=photo)
