"use strict";

/* =========================================================
   RASBHAV BOOKS
   MAIN JAVASCRIPT
========================================================= */


document.addEventListener("DOMContentLoaded", () => {

    loadFeaturedBooks();
    loadLatestBooks();
    loadPopularBooks();
    loadCategories();
    loadAuthors();

    setupNewsletterForm();

});


/* =========================================================
   API HELPER
========================================================= */

async function apiRequest(url, options = {}) {

    try {

        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(
                `Request failed: ${response.status}`
            );
        }

        return await response.json();

    } catch (error) {

        console.error(
            "Rasbhav API Error:",
            error
        );

        return null;
    }
}


/* =========================================================
   FEATURED BOOKS
========================================================= */

async function loadFeaturedBooks() {

    const container =
        document.getElementById("featured-books");

    if (!container) return;

    const data =
        await apiRequest("/api/books");

    if (!data || !Array.isArray(data)) {

        container.innerHTML = `
            <p class="loading">
                Unable to load books.
            </p>
        `;

        return;
    }


    const books = data.filter(
        book => book.featured === true
    );


    if (!books.length) {

        container.innerHTML = `
            <p class="loading">
                No featured books available.
            </p>
        `;

        return;
    }


    container.innerHTML =
        books
            .slice(0, 8)
            .map(createBookCard)
            .join("");

}


/* =========================================================
   LATEST BOOKS
========================================================= */

async function loadLatestBooks() {

    const container =
        document.getElementById("latest-books");

    if (!container) return;

    const data =
        await apiRequest("/api/books");


    if (!data || !Array.isArray(data)) {

        container.innerHTML = `
            <p class="loading">
                Unable to load books.
            </p>
        `;

        return;
    }


    container.innerHTML =
        data
            .slice(0, 8)
            .map(createBookCard)
            .join("");

}


/* =========================================================
   POPULAR BOOKS
========================================================= */

async function loadPopularBooks() {

    const container =
        document.getElementById("popular-books");

    if (!container) return;


    const data =
        await apiRequest("/api/books");


    if (!data || !Array.isArray(data)) {

        container.innerHTML = `
            <p class="loading">
                Unable to load books.
            </p>
        `;

        return;
    }


    /*
       Popular system will later use reading activity
       from the database.
       
       For now we display published books.
    */

    container.innerHTML =
        data
            .slice(0, 8)
            .map(createBookCard)
            .join("");

}


/* =========================================================
   BOOK CARD
========================================================= */

function createBookCard(book) {

    const cover =
        book.cover_image ||
        "/static/images/default-book.jpg";


    const author =
        book.author ||
        "Unknown Author";


    const language =
        book.language ||
        "";


    return `
        <article class="book-card">

            <a href="/books/${escapeHtml(book.slug)}">

                <img
                    src="${escapeHtml(cover)}"
                    alt="${escapeHtml(book.title)}"
                    class="book-cover"
                    loading="lazy"
                >

            </a>


            <div class="book-info">

                <h3>
                    <a href="/books/${escapeHtml(book.slug)}">
                        ${escapeHtml(book.title)}
                    </a>
                </h3>


                <p class="book-author">
                    ${escapeHtml(author)}
                </p>


                ${
                    language
                    ? `
                        <span class="book-language">
                            ${escapeHtml(language)}
                        </span>
                    `
                    : ""
                }


                <a
                    href="/books/${escapeHtml(book.slug)}"
                    class="btn btn-primary"
                >
                    Read Book
                </a>

            </div>

        </article>
    `;
}


/* =========================================================
   CATEGORIES
========================================================= */

async function loadCategories() {

    const container =
        document.getElementById("categories");

    if (!container) return;


    const data =
        await apiRequest("/api/categories");


    if (!data || !Array.isArray(data)) {

        container.innerHTML = `
            <p class="loading">
                Unable to load categories.
            </p>
        `;

        return;
    }


    if (!data.length) {

        container.innerHTML = `
            <p class="loading">
                No categories available.
            </p>
        `;

        return;
    }


    container.innerHTML =
        data
            .slice(0, 8)
            .map(category => {

                return `
                    <a
                        href="/category/${escapeHtml(category.slug)}"
                        class="category-card"
                    >

                        <div class="category-icon">
                            📚
                        </div>

                        <h3>
                            ${escapeHtml(category.name)}
                        </h3>

                        ${
                            category.description
                            ? `
                                <p>
                                    ${escapeHtml(
                                        category.description
                                    )}
                                </p>
                            `
                            : ""
                        }

                    </a>
                `;

            })
            .join("");

}


/* =========================================================
   AUTHORS
========================================================= */

async function loadAuthors() {

    const container =
        document.getElementById("authors");

    if (!container) return;


    const data =
        await apiRequest("/api/authors");


    if (!data || !Array.isArray(data)) {

        container.innerHTML = `
            <p class="loading">
                Unable to load authors.
            </p>
        `;

        return;
    }


    if (!data.length) {

        container.innerHTML = `
            <p class="loading">
                No authors available.
            </p>
        `;

        return;
    }


    container.innerHTML =
        data
            .slice(0, 8)
            .map(author => {

                const image =
                    author.profile_image ||
                    "/static/images/default-author.jpg";


                return `
                    <a
                        href="/author/${escapeHtml(author.slug)}"
                        class="author-card"
                    >

                        <img
                            src="${escapeHtml(image)}"
                            alt="${escapeHtml(author.name)}"
                            class="author-image"
                            loading="lazy"
                        >


                        <h3>
                            ${escapeHtml(author.name)}
                        </h3>


                        ${
                            author.biography
                            ? `
                                <p>
                                    ${escapeHtml(
                                        truncateText(
                                            author.biography,
                                            90
                                        )
                                    )}
                                </p>
                            `
                            : ""
                        }

                    </a>
                `;

            })
            .join("");

}


/* =========================================================
   NEWSLETTER
========================================================= */

function setupNewsletterForm() {

    const form =
        document.getElementById(
            "newsletter-form"
        );

    if (!form) return;


    form.addEventListener(
        "submit",
        event => {

            event.preventDefault();


            const email =
                document.getElementById(
                    "newsletter-email"
                ).value.trim();


            const message =
                document.getElementById(
                    "newsletter-message"
                );


            if (!email) {

                message.textContent =
                    "Please enter your email.";

                return;
            }


            message.textContent =
                "Thank you for subscribing!";


            form.reset();

        }
    );

}


/* =========================================================
   TEXT TRUNCATION
========================================================= */

function truncateText(text, length) {

    if (!text) return "";

    if (text.length <= length) {
        return text;
    }

    return text.substring(0, length) + "...";
}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHtml(value) {

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
