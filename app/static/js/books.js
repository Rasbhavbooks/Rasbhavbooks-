"use strict";


/* =========================================================
   GLOBAL
========================================================= */

let currentBook = null;
let currentChapters = [];


/* =========================================================
   API
========================================================= */

const BOOK_API_URL = `/api/books/${encodeURIComponent(BOOK_SLUG)}`;

const CHAPTER_API_URL =
    `/api/books/${encodeURIComponent(BOOK_SLUG)}/chapters`;


/* =========================================================
   DOM READY
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    loadBook();

    document.getElementById("currentYear").textContent =
        new Date().getFullYear();

});


/* =========================================================
   LOAD BOOK
========================================================= */

async function loadBook() {

    try {

        const response = await fetch(
            BOOK_API_URL,
            {
                method: "GET",
                credentials: "same-origin"
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.message || "Book not found."
            );

        }


        currentBook = data.book || data;


        renderBook(currentBook);

        await loadChapters();

    } catch (error) {

        console.error(error);

        showBookError();

    }

}


/* =========================================================
   RENDER BOOK
========================================================= */

function renderBook(book) {

    document.getElementById("bookLoading")
        .style.display = "none";

    document.getElementById("bookContent")
        .style.display = "block";


    const title =
        book.title || "Rasbhav Books";


    const description =
        book.short_description ||
        book.description ||
        `Read ${title} online on Rasbhav Books.`;


    /* TITLE */

    document.title =
        `${title} | Rasbhav Books`;


    /* META DESCRIPTION */

    setMeta(
        "metaDescription",
        "content",
        description.substring(0, 160)
    );


    /* ROBOTS */

    setMeta(
        "metaRobots",
        "content",
        "index, follow"
    );


    /* CANONICAL */

    const canonical =
        `${window.location.origin}/books/${encodeURIComponent(book.slug)}`;


    document.getElementById("canonicalUrl")
        .href = canonical;


    /* OG */

    setMeta(
        "ogTitle",
        "content",
        title
    );

    setMeta(
        "ogDescription",
        "content",
        description.substring(0, 200)
    );


    if (book.cover_image) {

        setMeta(
            "ogImage",
            "content",
            makeAbsoluteUrl(book.cover_image)
        );

    }


    /* BREADCRUMB */

    setText(
        "breadcrumbTitle",
        title
    );


    /* TITLE */

    setText(
        "bookTitle",
        title
    );


    /* SUBTITLE */

    const subtitle =
        document.getElementById("bookSubtitle");


    if (book.subtitle) {

        subtitle.textContent =
            book.subtitle;

        subtitle.style.display =
            "block";

    } else {

        subtitle.style.display =
            "none";

    }


    /* COVER */

    const cover =
        document.getElementById("bookCover");


    if (book.cover_image) {

        cover.src =
            makeAbsoluteUrl(book.cover_image);

        cover.alt =
            `${title} book cover`;

    } else {

        cover.style.display =
            "none";

    }


    /* LANGUAGE */

    setText(
        "bookLanguage",
        formatLanguage(book.language)
    );


    setText(
        "infoLanguage",
        formatLanguage(book.language)
    );


    /* STATUS */

    setText(
        "bookStatus",
        formatStatus(book.status)
    );


    setText(
        "infoStatus",
        formatStatus(book.status)
    );


    /* SHORT DESCRIPTION */

    setText(
        "bookShortDescription",
        book.short_description || ""
    );


    /* DESCRIPTION */

    const descriptionElement =
        document.getElementById("bookDescription");


    if (book.description) {

        descriptionElement.innerHTML =
            safeTextToHtml(book.description);

    } else {

        descriptionElement.innerHTML =
            "<p>No description available.</p>";

    }


    /* AUTHOR */

    setText(
        "infoAuthor",
        book.author_name ||
        book.author ||
        (
            book.author_id
                ? `Author #${book.author_id}`
                : "Unknown"
        )
    );


    /* PUBLISH DATE */

    setText(
        "infoPublishDate",
        formatDate(book.publish_date)
    );


    /* TAGS */

    renderTags(book.tags);


    /* BANNER */

    renderBanner(book);


    /* READ BUTTON */

    const readButton =
        document.getElementById("readBookButton");


    readButton.href =
        `/reader/${encodeURIComponent(book.slug)}`;

}


/* =========================================================
   LOAD CHAPTERS
========================================================= */

async function loadChapters() {

    const loading =
        document.getElementById("chaptersLoading");

    const empty =
        document.getElementById("chaptersEmpty");

    const list =
        document.getElementById("chaptersList");


    try {

        loading.style.display =
            "block";

        empty.style.display =
            "none";

        list.innerHTML =
            "";


        const response =
            await fetch(
                CHAPTER_API_URL,
                {
                    method: "GET",
                    credentials: "same-origin"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.message ||
                "Unable to load chapters."
            );

        }


        currentChapters =
            data.chapters || data || [];


        loading.style.display =
            "none";


        document.getElementById(
            "chapterCount"
        ).textContent =
            `${currentChapters.length} ${
                currentChapters.length === 1
                    ? "Chapter"
                    : "Chapters"
            }`;


        if (!currentChapters.length) {

            empty.style.display =
                "block";

            return;

        }


        renderChapters(currentChapters);

    } catch (error) {

        console.error(error);

        loading.style.display =
            "none";

        empty.textContent =
            "Unable to load chapters.";

        empty.style.display =
            "block";

    }

}


/* =========================================================
   RENDER CHAPTERS
========================================================= */

function renderChapters(chapters) {

    const list =
        document.getElementById("chaptersList");


    list.innerHTML =
        chapters.map((chapter, index) => {

            const number =
                chapter.chapter_number ||
                index + 1;


            const title =
                chapter.title ||
                chapter.chapter_title ||
                `Chapter ${number}`;


            const slug =
                chapter.slug ||
                "";


            const readerUrl =
                `/reader/${encodeURIComponent(
                    BOOK_SLUG
                )}?chapter=${encodeURIComponent(slug)}`;


            return `

                <a
                    href="${escapeAttribute(readerUrl)}"
                    class="chapter-card"
                >

                    <span class="chapter-number">
                        ${number}
                    </span>

                    <span class="chapter-content">

                        <strong>
                            ${escapeHtml(title)}
                        </strong>

                        ${
                            chapter.short_description
                                ? `
                                    <small>
                                        ${escapeHtml(
                                            chapter.short_description
                                        )}
                                    </small>
                                  `
                                : ""
                        }

                    </span>

                    <span class="chapter-arrow">
                        →
                    </span>

                </a>

            `;

        }).join("");

}


/* =========================================================
   TAGS
========================================================= */

function renderTags(tags) {

    const section =
        document.getElementById("tagsSection");

    const container =
        document.getElementById("bookTags");


    if (!tags) {

        section.style.display =
            "none";

        return;

    }


    let tagList = [];


    if (Array.isArray(tags)) {

        tagList = tags;

    } else {

        tagList =
            String(tags)
                .split(",")
                .map(tag => tag.trim())
                .filter(Boolean);

    }


    if (!tagList.length) {

        section.style.display =
            "none";

        return;

    }


    container.innerHTML =
        tagList.map(tag => {

            return `
                <span class="book-tag">
                    ${escapeHtml(tag)}
                </span>
            `;

        }).join("");


    section.style.display =
        "block";

}


/* =========================================================
   BANNER
========================================================= */

function renderBanner(book) {

    const section =
        document.getElementById(
            "bookBannerSection"
        );

    const image =
        document.getElementById(
            "bookBanner"
        );


    const banner =
        book.banner_image ||
        book.featured_image;


    if (!banner) {

        section.style.display =
            "none";

        return;

    }


    image.src =
        makeAbsoluteUrl(banner);


    image.alt =
        `${book.title || "Book"} banner`;


    section.style.display =
        "block";

}


/* =========================================================
   ERROR
========================================================= */

function showBookError() {

    document.getElementById(
        "bookLoading"
    ).style.display = "none";


    document.getElementById(
        "bookContent"
    ).style.display = "none";


    document.getElementById(
        "bookError"
    ).style.display = "block";

}


/* =========================================================
   HELPERS
========================================================= */

function setText(id, value) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value || "—";

    }

}


function setMeta(id, attribute, value) {

    const element =
        document.getElementById(id);


    if (element) {

        element.setAttribute(
            attribute,
            value || ""
        );

    }

}


function formatLanguage(language) {

    if (!language) {
        return "—";
    }


    const languages = {

        gujarati: "Gujarati",

        hindi: "Hindi",

        english: "English"

    };


    return languages[
        String(language).toLowerCase()
    ] || language;

}


function formatStatus(status) {

    if (!status) {
        return "—";
    }


    return String(status)
        .charAt(0)
        .toUpperCase()
        +
        String(status)
            .slice(1);

}


function formatDate(value) {

    if (!value) {
        return "—";
    }


    const date =
        new Date(value);


    if (Number.isNaN(date.getTime())) {

        return value;

    }


    return date.toLocaleDateString(
        "en-IN",
        {
            day: "numeric",
            month: "long",
            year: "numeric"
        }
    );

}


function makeAbsoluteUrl(url) {

    if (!url) {
        return "";
    }


    try {

        return new URL(
            url,
            window.location.origin
        ).href;

    } catch {

        return url;

    }

}


function safeTextToHtml(text) {

    return escapeHtml(text)
        .replace(/\n\n+/g, "</p><p>")
        .replace(/\n/g, "<br>")
        .replace(/^/, "<p>")
        .replace(/$/, "</p>");

}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function escapeAttribute(value) {

    return escapeHtml(value);

}
