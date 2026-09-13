from flask import Blueprint, render_template

from app.models.book import Book
from app.models.seo import SEO


public_bp = Blueprint(
    "public",
    __name__
)


@public_bp.route("/")
def home():
    return render_template(
        "public/index.html"
    )


@public_bp.route("/books")
def books():
    return render_template(
        "public/books.html"
    )


@public_bp.route("/books/<slug>")
def book_detail(slug):

    book = Book.query.filter_by(
        slug=slug,
        published=True
    ).first_or_404()

    seo = SEO.query.filter_by(
        entity_type="book",
        entity_id=book.id
    ).first()

    return render_template(
        "public/book-detail.html",
        book=book,
        seo=seo,
        slug=slug
    )


@public_bp.route("/category/<slug>")
def category(slug):
    return render_template(
        "public/category.html",
        slug=slug
    )


@public_bp.route("/author/<slug>")
def author(slug):
    return render_template(
        "public/author.html",
        slug=slug
    )


@public_bp.route("/search")
def search():
    return render_template(
        "public/search.html"
    )


@public_bp.route("/library")
def library():
    return render_template(
        "public/library.html"
    )


@public_bp.route("/favorites")
def favorites():
    return render_template(
        "public/favorites.html"
    )


@public_bp.route("/bookmarks")
def bookmarks():
    return render_template(
        "public/bookmarks.html"
    )


@public_bp.route("/reader/<slug>")
def reader(slug):
    return render_template(
        "public/reader.html",
        slug=slug
    )
