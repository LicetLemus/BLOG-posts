from flask import Blueprint, request, flash, redirect, url_for, g, render_template
from blogr.auth import login_required
from blogr.models import Post
from blogr import db

bp = Blueprint("post", __name__, url_prefix="/post")


@bp.route("/posts")
@login_required
def posts():
    posts = Post.query.all()
    return render_template("admin/posts.html", posts=posts)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        url = request.form.get("url")
        url = url.replace(" ", "-")
        title = request.form.get("title")
        info = request.form.get("info")
        content = request.form.get("ckeditor")

        post = Post(g.user.id, url, title, info, content)

        error = None

        post_url = Post.query.filter_by(url=url).first()

        if post_url == None:
            db.session.add(post)
            db.session.commit()
            flash(f"La entrada {post.title} ha sido creada", "success")
            return redirect(url_for("post.posts"))
        else:
            flash(f"La entrada {post.title} ya existe", "error")
        flash(error)

    return render_template("admin/create.html")


@bp.route("/update")
def update():
    return "Pagina del actualizar"
