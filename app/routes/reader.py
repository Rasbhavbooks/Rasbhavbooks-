from flask import Blueprint, jsonify
from app.models.book import Book
from app.models.chapter import Chapter


reader_bp = Blueprint(
    "reader",
    __name__,
    url_prefix="/api/reader"
)


@reader_bp.route("/<book_slug>/chapters", methods=["GET"])
def get_reader_chapters(book_slug):
    book = Book.query.filter_by(
        slug=book_slug,
        published=True
    ).first_or_404()

    chapters = Chapter.query.filter_by(
        book_id=book.id,
        status="published"
    ).order_by(
        Chapter.chapter_number.asc()
    ).all()

    return jsonify([
        {
            "id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "slug": chapter.slug
        }
        for chapter in chapters
    ])


@reader_bp.route(
    "/<book_slug>/chapter/<int:chapter_number>",
    methods=["GET"]
)
def get_chapter(book_slug, chapter_number):
    book = Book.query.filter_by(
        slug=book_slug,
        published=True
    ).first_or_404()

    chapter = Chapter.query.filter_by(
        book_id=book.id,
        chapter_number=chapter_number,
        status="published"
    ).first_or_404()

    previous_chapter = Chapter.query.filter(
        Chapter.book_id == book.id,
        Chapter.chapter_number < chapter_number,
        Chapter.status == "published"
    ).order_by(
        Chapter.chapter_number.desc()
    ).first()

    next_chapter = Chapter.query.filter(
        Chapter.book_id == book.id,
        Chapter.chapter_number > chapter_number,
        Chapter.status == "published"
    ).order_by(
        Chapter.chapter_number.asc()
    ).first()

    return jsonify({
        "book": {
            "id": book.id,
            "title": book.title,
            "slug": book.slug
        },
        "chapter": {
            "id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "slug": chapter.slug,
            "content": chapter.content
        },
        "previous": {
            "chapter_number": previous_chapter.chapter_number,
            "title": previous_chapter.title,
            "slug": previous_chapter.slug
        } if previous_chapter else None,
        "next": {
            "chapter_number": next_chapter.chapter_number,
            "title": next_chapter.title,
            "slug": next_chapter.slug
        } if next_chapter else None
    })
