/* =========================================================
   RASBHAV BOOKS
   PUBLIC BOOK JAVASCRIPT
   ========================================================= */

"use strict";

/* =========================================================
   API CONFIG
   ========================================================= */

const BOOK_API_URL = "/api/books/";
const READER_API_URL = "/api/reader/";


/* =========================================================
   GLOBAL STATE
   ========================================================= */

const BooksState = {
    currentBook: null,
    chapters: [],
    currentChapter: null
};


/* =========================================================
   HELPERS
   ========================================================= */

function escapeHTML(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function getSlugFromURL() {
    const parts = window.location.pathname.split("/").filter(Boolean);

    if (parts.length >= 2 && parts[0] === "books") {
        return decodeURIComponent(parts[1]);
    }

    if (parts.length >= 2 && parts[0] === "reader") {
        return decodeURIComponent(parts[1]);
    }

    return null;
}


function showLoading(element) {
    if (!element) return;

    element.innerHTML = `
        <div class="loading-state">
            <div class="loader"></div>
            <p>Loading...</p>
        </div>
    `;
}


function showError(element, message = "Something went wrong.") {
    if (!element) return;

    element.innerHTML = `
        <div class="error-state">
            <h3>Unable to load</h3>
            <p>${escapeHTML(message)}</p>
        </div>
    `;
}


/* =========================================================
   FETCH BOOK
   ========================================================= */

async function loadBook(slug) {

    if (!slug) {
        console.error("Book slug not found.");
        return null;
    }

    try {

        const response = await fetch(
            `${BOOK_API_URL}${encodeURIComponent(slug)}`,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error(`Book API error: ${response.status}`);
        }

        const data = await response.json();

        BooksState.currentBook = data;

        return data;

    } catch (error) {

        console.error("loadBook():", error);

        return null;
    }
}


/* =========================================================
   FETCH CHAPTERS
   IMPORTANT:
   Chapters come from /api/reader/
   ========================================================= */

async function loadChapters(slug) {

    if (!slug) {
        console.error("Book slug not found.");
        return [];
    }

    try {

        const response = await fetch(
            `${READER_API_URL}${encodeURIComponent(slug)}/chapters`,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error(`Chapter API error: ${response.status}`);
        }

        const data = await response.json();

        let chapters = [];

        if (Array.isArray(data)) {
            chapters = data;
        } else if (Array.isArray(data.chapters)) {
            chapters = data.chapters;
        } else if (Array.isArray(data.data)) {
            chapters = data.data;
        }

        BooksState.chapters = chapters;

        return chapters;

    } catch (error) {

        console.error("loadChapters():", error);

        BooksState.chapters = [];

        return [];
    }
}


/* =========================================================
   UPDATE SEO
   ========================================================= */

function updateMetaTag(attribute, value, content) {

    if (!value || !content) {
        return;
    }

    let element = document.head.querySelector(
        `meta[${attribute}="${CSS.escape(value)}"]`
    );

    if (!element) {

        element = document.createElement("meta");

        element.setAttribute(attribute, value);

        document.head.appendChild(element);
    }

    element.setAttribute("content", content);
}


function updateSEO(book) {

    if (!book) {
        return;
    }

    const title =
        book.meta_title ||
        book.seo_title ||
        book.title ||
        "Rasbhav Books";

    const description =
        book.meta_description ||
        book.seo_description ||
        book.short_description ||
        book.description ||
        "";

    document.title = title;

    updateMetaTag(
        "name",
        "description",
        description
    );

    if (book.robots) {

        updateMetaTag(
            "name",
            "robots",
            book.robots
        );
    }

    if (book.canonical_url) {

        let canonical =
            document.head.querySelector(
                'link[rel="canonical"]'
            );

        if (!canonical) {

            canonical = document.createElement("link");

            canonical.rel = "canonical";

            document.head.appendChild(canonical);
        }

        canonical.href = book.canonical_url;
    }

    updateMetaTag(
        "property",
        "og:title",
        book.og_title || title
    );

    updateMetaTag(
        "property",
        "og:description",
        book.og_description || description
    );

    if (book.og_image) {

        updateMetaTag(
            "property",
            "og:image",
            book.og_image
        );
    }
}


/* =========================================================
   RENDER CHAPTER LIST
   ========================================================= */

function renderChapters(chapters, container) {

    if (!container) {
        return;
    }

    if (!Array.isArray(chapters) || chapters.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                <p>No chapters available.</p>
            </div>
        `;

        return;
    }

    container.innerHTML = chapters.map((chapter, index) => {

        const chapterId =
            chapter.id !== undefined
                ? chapter.id
                : "";

        const number =
            chapter.chapter_number ||
            index + 1;

        const title =
            chapter.title ||
            `Chapter ${number}`;

        return `
            <article class="chapter-item"
                     data-chapter-id="${escapeHTML(chapterId)}">

                <div class="chapter-number">
                    ${escapeHTML(number)}
                </div>

                <div class="chapter-info">

                    <h3>
                        ${escapeHTML(title)}
                    </h3>

                    ${
                        chapter.short_description
                            ? `<p>${escapeHTML(chapter.short_description)}</p>`
                            : ""
                    }

                </div>

                <a
                    class="chapter-read-btn"
                    href="/reader/${encodeURIComponent(
                        getSlugFromURL() || ""
                    )}?chapter=${encodeURIComponent(chapterId)}"
                >
                    Read
                </a>

            </article>
        `;

    }).join("");
}


/* =========================================================
   BOOK DETAIL PAGE
   ========================================================= */

async function initBookDetailPage() {

    const slug = getSlugFromURL();

    if (!slug) {
        return;
    }

    const chaptersContainer =
        document.querySelector("#chapters-container") ||
        document.querySelector(".chapters-list") ||
        document.querySelector("[data-chapters]");

    if (chaptersContainer) {
        showLoading(chaptersContainer);
    }

    const book = await loadBook(slug);

    if (book) {
        updateSEO(book);
    }

    const chapters = await loadChapters(slug);

    if (chaptersContainer) {
        renderChapters(
            chapters,
            chaptersContainer
        );
    }
}


/* =========================================================
   FAVORITES
   ========================================================= */

function getFavorites() {

    try {

        const data =
            localStorage.getItem("rasbhav_favorites");

        return data
            ? JSON.parse(data)
            : [];

    } catch (error) {

        console.error(error);

        return [];
    }
}


function saveFavorites(favorites) {

    localStorage.setItem(
        "rasbhav_favorites",
        JSON.stringify(favorites)
    );
}


function toggleFavorite(bookId) {

    if (!bookId) {
        return false;
    }

    const favorites = getFavorites();

    const index =
        favorites.indexOf(bookId);

    let active = false;

    if (index === -1) {

        favorites.push(bookId);

        active = true;

    } else {

        favorites.splice(index, 1);
    }

    saveFavorites(favorites);

    return active;
}


function isFavorite(bookId) {

    return getFavorites().includes(bookId);
}


/* =========================================================
   BOOKMARKS
   ========================================================= */

function getBookmarks() {

    try {

        const data =
            localStorage.getItem("rasbhav_bookmarks");

        return data
            ? JSON.parse(data)
            : [];

    } catch (error) {

        console.error(error);

        return [];
    }
}


function saveBookmarks(bookmarks) {

    localStorage.setItem(
        "rasbhav_bookmarks",
        JSON.stringify(bookmarks)
    );
}


function toggleBookmark(bookId, chapterId = null) {

    if (!bookId) {
        return false;
    }

    const bookmarks = getBookmarks();

    const existingIndex =
        bookmarks.findIndex(item =>
            String(item.book_id) === String(bookId) &&
            String(item.chapter_id || "") ===
            String(chapterId || "")
        );

    let active = false;

    if (existingIndex === -1) {

        bookmarks.push({
            book_id: bookId,
            chapter_id: chapterId,
            created_at: new Date().toISOString()
        });

        active = true;

    } else {

        bookmarks.splice(
            existingIndex,
            1
        );
    }

    saveBookmarks(bookmarks);

    return active;
}


/* =========================================================
   READING PROGRESS
   ========================================================= */

function getReadingProgress() {

    try {

        const data =
            localStorage.getItem(
                "rasbhav_reading_progress"
            );

        return data
            ? JSON.parse(data)
            : {};

    } catch (error) {

        console.error(error);

        return {};
    }
}


function saveReadingProgress(
    bookId,
    chapterId,
    progress = 0
) {

    if (!bookId) {
        return;
    }

    const data =
        getReadingProgress();

    data[String(bookId)] = {

        chapter_id: chapterId,

        progress: Math.max(
            0,
            Math.min(100, Number(progress) || 0)
        ),

        updated_at:
            new Date().toISOString()
    };

    localStorage.setItem(
        "rasbhav_reading_progress",
        JSON.stringify(data)
    );
}


/* =========================================================
   BUTTON EVENTS
   ========================================================= */

document.addEventListener(
    "click",
    function (event) {

        const favoriteButton =
            event.target.closest(
                "[data-favorite-book]"
            );

        if (favoriteButton) {

            const bookId =
                favoriteButton.dataset.favoriteBook;

            const active =
                toggleFavorite(bookId);

            favoriteButton.classList.toggle(
                "active",
                active
            );

            favoriteButton.setAttribute(
                "aria-pressed",
                active ? "true" : "false"
            );

            return;
        }


        const bookmarkButton =
            event.target.closest(
                "[data-bookmark-book]"
            );

        if (bookmarkButton) {

            const bookId =
                bookmarkButton.dataset.bookmarkBook;

            const chapterId =
                bookmarkButton.dataset.chapterId ||
                null;

            const active =
                toggleBookmark(
                    bookId,
                    chapterId
                );

            bookmarkButton.classList.toggle(
                "active",
                active
            );

            bookmarkButton.setAttribute(
                "aria-pressed",
                active ? "true" : "false"
            );
        }

    }
);


/* =========================================================
   INITIALIZE
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const isBookDetail =
            document.body.classList.contains(
                "book-detail-page"
            ) ||
            document.querySelector(
                ".book-detail-section"
            );

        if (isBookDetail) {

            initBookDetailPage();
        }

    }
);


/* =========================================================
   GLOBAL EXPORT
   ========================================================= */

window.RasbhavBooks = {

    loadBook,
    loadChapters,

    updateSEO,

    getFavorites,
    saveFavorites,
    toggleFavorite,
    isFavorite,

    getBookmarks,
    saveBookmarks,
    toggleBookmark,

    getReadingProgress,
    saveReadingProgress

};
