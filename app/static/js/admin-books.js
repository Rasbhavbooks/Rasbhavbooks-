/* =========================================================
   RASBHAV BOOKS
   ADMIN BOOKS CMS JAVASCRIPT
   =========================================================

   File:
   app/static/js/admin-books.js

   API:
   /api/admin/books
   /api/admin/authors
   /api/admin/categories

   Features:
   - Book listing
   - Search
   - Status filter
   - Published filter
   - Featured filter
   - Create book
   - Edit book
   - Delete book
   - Publish / Unpublish
   - Featured / Unfeatured
   - Author selection
   - Multiple categories
   - Publish date
   - SEO
   - JSON-LD
   - Validation
   - Toast messages
   - Modal
   - Mobile friendly DOM
   - Safe API handling

   IMPORTANT:
   No CSS is written in this file.
========================================================= */

"use strict";


/* =========================================================
   1. GLOBAL STATE
========================================================= */

const AdminBooksState = {

    books: [],

    authors: [],

    categories: [],

    editingBookId: null,

    deletingBookId: null,

    loading: false,

    searchTimer: null,

    initialized: false

};


/* =========================================================
   2. API HELPER
========================================================= */

async function adminBooksRequest(url, options = {}) {

    const config = {

        credentials: "same-origin",

        ...options,

        headers: {

            "Content-Type": "application/json",

            ...(options.headers || {})

        }

    };

    try {

        const response = await fetch(
            url,
            config
        );

        let data;

        const contentType =
            response.headers.get("content-type") || "";

        if (
            contentType.includes("application/json")
        ) {

            data = await response.json();

        } else {

            const text =
                await response.text();

            data = {

                success: response.ok,

                message:
                    text ||
                    "Unknown server response."

            };

        }


        if (!response.ok) {

            throw new Error(

                data?.message ||
                data?.error ||
                `Request failed (${response.status}).`

            );

        }


        if (
            data &&
            data.success === false
        ) {

            throw new Error(

                data.message ||
                data.error ||
                "Request failed."

            );

        }


        return data;

    } catch (error) {

        console.error(
            "Admin Books API Error:",
            error
        );

        throw error;

    }

}


/* =========================================================
   3. DOM HELPERS
========================================================= */

function adminBookElement(id) {

    return document.getElementById(id);

}


function adminBookValue(id) {

    const element =
        adminBookElement(id);

    if (!element) {

        return "";

    }

    return element.value;

}


function adminBookSetValue(id, value) {

    const element =
        adminBookElement(id);

    if (!element) {

        return;

    }

    element.value =
        value === null ||
        value === undefined
            ? ""
            : value;

}


function adminBookChecked(id) {

    const element =
        adminBookElement(id);

    return element
        ? Boolean(element.checked)
        : false;

}


function adminBookSetChecked(id, value) {

    const element =
        adminBookElement(id);

    if (!element) {

        return;

    }

    element.checked =
        Boolean(value);

}


/* =========================================================
   4. HTML ESCAPE
========================================================= */

function escapeAdminBookHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");

}


/* =========================================================
   5. TOAST
========================================================= */

function showAdminBookToast(
    message,
    type = "success"
) {

    let container =
        document.querySelector(
            ".admin-toast-container"
        );

    if (!container) {

        container =
            document.createElement("div");

        container.className =
            "admin-toast-container";

        document.body.appendChild(
            container
        );

    }


    const toast =
        document.createElement("div");

    toast.className =
        `admin-toast ${type}`;

    toast.textContent =
        message;

    container.appendChild(
        toast
    );


    setTimeout(() => {

        toast.classList.add(
            "is-hiding"
        );

        setTimeout(() => {

            toast.remove();

        }, 250);

    }, 3000);

}


/* =========================================================
   6. INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        if (
            AdminBooksState.initialized
        ) {

            return;

        }

        AdminBooksState.initialized =
            true;

        initializeAdminBooks();

    }
);


/* =========================================================
   7. INITIALIZE
========================================================= */

async function initializeAdminBooks() {

    bindAdminBookEvents();

    createAdminBookModalIfMissing();

    setAdminBookLoading(true);

    try {

        await Promise.all([

            loadAdminAuthors(),

            loadAdminCategories()

        ]);


        await loadAdminBooks();

    } catch (error) {

        console.error(error);

        showAdminBookToast(

            error.message ||
            "Books module could not be loaded.",

            "error"

        );

    } finally {

        setAdminBookLoading(false);

    }

}


/* =========================================================
   8. EVENT BINDINGS
========================================================= */

function bindAdminBookEvents() {

    const search =
        adminBookElement(
            "bookSearch"
        );

    if (search) {

        search.addEventListener(
            "input",
            () => {

                clearTimeout(
                    AdminBooksState.searchTimer
                );

                AdminBooksState.searchTimer =
                    setTimeout(
                        () => {

                            loadAdminBooks();

                        },
                        350
                    );

            }
        );

    }


    const statusFilter =
        adminBookElement(
            "bookStatusFilter"
        );

    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            loadAdminBooks
        );

    }


    const publishedFilter =
        adminBookElement(
            "bookPublishedFilter"
        );

    if (publishedFilter) {

        publishedFilter.addEventListener(
            "change",
            loadAdminBooks
        );

    }


    const featuredFilter =
        adminBookElement(
            "bookFeaturedFilter"
        );

    if (featuredFilter) {

        featuredFilter.addEventListener(
            "change",
            loadAdminBooks
        );

    }


    const addButton =
        adminBookElement(
            "addBookBtn"
        );

    if (addButton) {

        addButton.addEventListener(
            "click",
            openAdminBookModal
        );

    }


    document.addEventListener(
        "click",
        handleAdminBookDocumentClick
    );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape"
            ) {

                closeAdminBookModal();

                closeAdminBookConfirm();

            }

        }
    );

}


/* =========================================================
   9. DOCUMENT CLICK HANDLER
========================================================= */

function handleAdminBookDocumentClick(event) {

    const editButton =
        event.target.closest(
            "[data-book-edit]"
        );

    if (editButton) {

        const id =
            Number(
                editButton.dataset.bookEdit
            );

        editAdminBook(id);

        return;

    }


    const deleteButton =
        event.target.closest(
            "[data-book-delete]"
        );

    if (deleteButton) {

        const id =
            Number(
                deleteButton.dataset.bookDelete
            );

        deleteAdminBook(id);

        return;

    }


    const publishButton =
        event.target.closest(
            "[data-book-publish]"
        );

    if (publishButton) {

        const id =
            Number(
                publishButton.dataset.bookPublish
            );

        toggleAdminBookPublished(id);

        return;

    }


    const featuredButton =
        event.target.closest(
            "[data-book-featured]"
        );

    if (featuredButton) {

        const id =
            Number(
                featuredButton.dataset.bookFeatured
            );

        toggleAdminBookFeatured(id);

        return;

    }


    const closeButton =
        event.target.closest(
            "[data-close-book-modal]"
        );

    if (closeButton) {

        closeAdminBookModal();

        return;

    }


    const confirmDelete =
        event.target.closest(
            "[data-confirm-book-delete]"
        );

    if (confirmDelete) {

        confirmAdminBookDelete();

        return;

    }


    const cancelDelete =
        event.target.closest(
            "[data-cancel-book-delete]"
        );

    if (cancelDelete) {

        closeAdminBookConfirm();

        return;

    }


    const overlay =
        event.target.closest(
            ".admin-modal-overlay"
        );

    if (
        overlay &&
        event.target === overlay
    ) {

        if (
            overlay.id === "bookModal"
        ) {

            closeAdminBookModal();

        }

        if (
            overlay.id === "bookConfirmModal"
        ) {

            closeAdminBookConfirm();

        }

    }

}


/* =========================================================
   10. LOAD BOOKS
========================================================= */

async function loadAdminBooks() {

    if (
        AdminBooksState.loading
    ) {

        return;

    }

    AdminBooksState.loading =
        true;

    setAdminBookLoading(true);

    try {

        const params =
            new URLSearchParams();


        const search =
            adminBookValue(
                "bookSearch"
            ).trim();

        if (search) {

            params.set(
                "search",
                search
            );

        }


        const status =
            adminBookValue(
                "bookStatusFilter"
            );

        if (status) {

            params.set(
                "status",
                status
            );

        }


        const published =
            adminBookValue(
                "bookPublishedFilter"
            );

        if (
            published !== ""
        ) {

            params.set(
                "published",
                published
            );

        }


        const featured =
            adminBookValue(
                "bookFeaturedFilter"
            );

        if (
            featured !== ""
        ) {

            params.set(
                "featured",
                featured
            );

        }


        params.set(
            "limit",
            "200"
        );


        const query =
            params.toString();


        const url =
            `/api/admin/books?${query}`;


        const data =
            await adminBooksRequest(
                url
            );


        const books =
            Array.isArray(data.books)
                ? data.books
                : Array.isArray(data.results)
                    ? data.results
                    : Array.isArray(data.data)
                        ? data.data
                        : [];


        AdminBooksState.books =
            books;


        renderAdminBooks(
            books
        );


        updateAdminBookCount(
            books.length
        );


    } catch (error) {

        console.error(error);

        renderAdminBooksError(
            error.message
        );

        showAdminBookToast(
            error.message ||
            "Unable to load books.",
            "error"
        );

    } finally {

        AdminBooksState.loading =
            false;

        setAdminBookLoading(false);

    }

}


/* =========================================================
   11. LOAD AUTHORS
========================================================= */

async function loadAdminAuthors() {

    try {

        const data =
            await adminBooksRequest(
                "/api/admin/authors"
            );


        const authors =
            Array.isArray(data.authors)
                ? data.authors
                : Array.isArray(data.results)
                    ? data.results
                    : Array.isArray(data.data)
                        ? data.data
                        : [];


        AdminBooksState.authors =
            authors;


        populateAdminAuthors(
            authors
        );

    } catch (error) {

        console.warn(
            "Authors could not be loaded:",
            error
        );

    }

}


/* =========================================================
   12. LOAD CATEGORIES
========================================================= */

async function loadAdminCategories() {

    try {

        const data =
            await adminBooksRequest(
                "/api/admin/categories"
            );


        const categories =
            Array.isArray(data.categories)
                ? data.categories
                : Array.isArray(data.results)
                    ? data.results
                    : Array.isArray(data.data)
                        ? data.data
                        : [];


        AdminBooksState.categories =
            categories;


        populateAdminCategories(
            categories
        );

    } catch (error) {

        console.warn(
            "Categories could not be loaded:",
            error
        );

    }

}


/* =========================================================
   13. POPULATE AUTHORS
========================================================= */

function populateAdminAuthors(
    authors
) {

    const select =
        adminBookElement(
            "bookAuthor"
        );

    if (!select) {

        return;

    }


    const current =
        select.value;


    select.innerHTML =
        `
        <option value="">
            Select Author
        </option>
        `;


    authors.forEach(
        author => {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                author.id;

            option.textContent =
                author.name ||
                `Author #${author.id}`;

            select.appendChild(
                option
            );

        }
    );


    if (current) {

        select.value =
            current;

    }

}


/* =========================================================
   14. POPULATE CATEGORIES
========================================================= */

function populateAdminCategories(
    categories
) {

    const container =
        adminBookElement(
            "bookCategories"
        );

    if (!container) {

        return;

    }


    container.innerHTML =
        "";


    categories.forEach(
        category => {

            const label =
                document.createElement(
                    "label"
                );

            label.className =
                "admin-category-option";


            const checkbox =
                document.createElement(
                    "input"
                );

            checkbox.type =
                "checkbox";

            checkbox.name =
                "category_ids";

            checkbox.value =
                category.id;


            const text =
                document.createElement(
                    "span"
                );

            text.textContent =
                category.name ||
                `Category #${category.id}`;


            label.appendChild(
                checkbox
            );

            label.appendChild(
                text
            );


            container.appendChild(
                label
            );

        }
    );

}


/* =========================================================
   15. RENDER BOOKS
========================================================= */

function renderAdminBooks(
    books
) {

    const tbody =
        adminBookElement(
            "booksTableBody"
        );

    if (!tbody) {

        return;

    }


    if (
        !Array.isArray(books) ||
        books.length === 0
    ) {

        tbody.innerHTML =
            `
            <tr>
                <td
                    colspan="8"
                    class="admin-empty-state"
                >
                    No books found.
                </td>
            </tr>
            `;

        return;

    }


    tbody.innerHTML =
        books.map(
            book => {

                const author =
                    book.author?.name ||
                    getAuthorName(
                        book.author_id
                    ) ||
                    "—";


                const categories =
                    Array.isArray(
                        book.categories
                    )
                        ? book.categories
                            .map(
                                category =>
                                    category.name
                            )
                            .filter(Boolean)
                            .join(", ")
                        : "—";


                const cover =
                    book.cover_image
                        ? `
                            <img
                                src="${escapeAdminBookHTML(book.cover_image)}"
                                alt="${escapeAdminBookHTML(book.title)}"
                                class="admin-book-cover"
                                loading="lazy"
                            >
                          `
                        : `
                            <div class="admin-book-cover-placeholder">
                                📖
                            </div>
                          `;


                const published =
                    Boolean(
                        book.published
                    );


                const featured =
                    Boolean(
                        book.featured
                    );


                const status =
                    book.status ||
                    "draft";


                return `

                    <tr>

                        <td>

                            <div class="admin-book-info">

                                ${cover}

                                <div>

                                    <strong>
                                        ${escapeAdminBookHTML(book.title)}
                                    </strong>

                                    <small>
                                        ${escapeAdminBookHTML(book.slug || "")}
                                    </small>

                                </div>

                            </div>

                        </td>


                        <td>
                            ${escapeAdminBookHTML(author)}
                        </td>


                        <td>
                            ${escapeAdminBookHTML(book.language || "—")}
                        </td>


                        <td>
                            ${escapeAdminBookHTML(categories)}
                        </td>


                        <td>

                            <span
                                class="admin-status-badge ${
                                    published
                                        ? "published"
                                        : "draft"
                                }"
                            >

                                ${
                                    published
                                        ? "Published"
                                        : "Draft"
                                }

                            </span>

                        </td>


                        <td>

                            <span
                                class="admin-status-badge ${
                                    featured
                                        ? "featured"
                                        : "normal"
                                }"
                            >

                                ${
                                    featured
                                        ? "Featured"
                                        : "Normal"
                                }

                            </span>

                        </td>


                        <td>

                            <span
                                class="admin-status-badge status-${escapeAdminBookHTML(status)}"
                            >

                                ${escapeAdminBookHTML(status)}

                            </span>

                        </td>


                        <td>

                            <div class="admin-book-actions">

                                <button
                                    type="button"
                                    class="admin-btn admin-btn-small"
                                    data-book-edit="${book.id}"
                                >
                                    Edit
                                </button>


                                <button
                                    type="button"
                                    class="admin-btn admin-btn-small"
                                    data-book-publish="${book.id}"
                                >
                                    ${
                                        published
                                            ? "Unpublish"
                                            : "Publish"
                                    }
                                </button>


                                <button
                                    type="button"
                                    class="admin-btn admin-btn-small"
                                    data-book-featured="${book.id}"
                                >
                                    ${
                                        featured
                                            ? "Unfeature"
                                            : "Feature"
                                    }
                                </button>


                                <button
                                    type="button"
                                    class="admin-btn admin-btn-small admin-btn-danger"
                                    data-book-delete="${book.id}"
                                >
                                    Delete
                                </button>

                            </div>

                        </td>

                    </tr>

                `;

            }
        ).join("");

}


/* =========================================================
   16. GET AUTHOR NAME
========================================================= */

function getAuthorName(
    authorId
) {

    if (!authorId) {

        return "";

    }


    const author =
        AdminBooksState.authors.find(
            item =>
                Number(item.id) ===
                Number(authorId)
        );


    return author?.name || "";

}


/* =========================================================
   17. RENDER ERROR
========================================================= */

function renderAdminBooksError(
    message
) {

    const tbody =
        adminBookElement(
            "booksTableBody"
        );

    if (!tbody) {

        return;

    }


    tbody.innerHTML =
        `
        <tr>
            <td
                colspan="8"
                class="admin-error-state"
            >
                ${
                    escapeAdminBookHTML(
                        message ||
                        "Unable to load books."
                    )
                }
            </td>
        </tr>
        `;

}


/* =========================================================
   18. UPDATE COUNT
========================================================= */

function updateAdminBookCount(
    count
) {

    const elements =
        document.querySelectorAll(
            "[data-books-count]"
        );


    elements.forEach(
        element => {

            element.textContent =
                count;

        }
    );


    const countElement =
        adminBookElement(
            "bookCount"
        );

    if (countElement) {

        countElement.textContent =
            count;

    }

}


/* =========================================================
   19. LOADING STATE
========================================================= */

function setAdminBookLoading(
    loading
) {

    const loadingElement =
        adminBookElement(
            "booksLoading"
        );


    if (loadingElement) {

        loadingElement.hidden =
            !loading;

    }


    const table =
        adminBookElement(
            "booksTable"
        );


    if (table) {

        table.classList.toggle(
            "is-loading",
            loading
        );

    }

}


/* =========================================================
   20. CREATE MODAL
========================================================= */

function createAdminBookModalIfMissing() {

    if (
        adminBookElement(
            "bookModal"
        )
    ) {

        return;

    }


    const modal =
        document.createElement(
            "div"
        );

    modal.id =
        "bookModal";

    modal.className =
        "admin-modal-overlay";

    modal.hidden =
        true;


    modal.innerHTML =
        `

        <div
            class="admin-modal admin-book-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="bookModalTitle"
        >

            <div class="admin-modal-header">

                <div>

                    <h2 id="bookModalTitle">
                        Add Book
                    </h2>

                    <p>
                        Manage book content, categories and SEO.
                    </p>

                </div>

                <button
                    type="button"
                    class="admin-modal-close"
                    data-close-book-modal
                    aria-label="Close"
                >
                    ×
                </button>

            </div>


            <form
                id="bookForm"
                class="admin-book-form"
            >

                <div class="admin-form-section">

                    <h3>
                        Basic Information
                    </h3>


                    <div class="admin-form-grid">

                        <div class="admin-form-group admin-form-full">

                            <label for="bookTitle">
                                Title *
                            </label>

                            <input
                                type="text"
                                id="bookTitle"
                                required
                                maxlength="255"
                            >

                        </div>


                        <div class="admin-form-group">

                            <label for="bookSlug">
                                Slug *
                            </label>

                            <input
                                type="text"
                                id="bookSlug"
                                required
                                maxlength="255"
                            >

                        </div>


                        <div class="admin-form-group">

                            <label for="bookSubtitle">
                                Subtitle
                            </label>

                            <input
                                type="text"
                                id="bookSubtitle"
                                maxlength="255"
                            >

                        </div>


                        <div class="admin-form-group admin-form-full">

                            <label for="bookShortDescription">
                                Short Description
                            </label>

                            <textarea
                                id="bookShortDescription"
                                rows="3"
                            ></textarea>

                        </div>


                        <div class="admin-form-group admin-form-full">

                            <label for="bookDescription">
                                Description
                            </label>

                            <textarea
                                id="bookDescription"
                                rows="7"
                            ></textarea>

                        </div>

                    </div>

                </div>


                <div class="admin-form-section">

                    <h3>
                        Author & Categories
                    </h3>


                    <div class="admin-form-grid">

                        <div class="admin-form-group">

                            <label for="bookAuthor">
                                Author
                            </label>

                            <select id="bookAuthor">

                                <option value="">
                                    Select Author
                                </option>

                            </select>

                        </div>


                        <div class="admin-form-group">

                            <label for="bookLanguage">
                                Language
                            </label>

                            <select id="bookLanguage">

                                <option value="">
                                    Select Language
                                </option>

                                <option value="Gujarati">
                                    Gujarati
                                </option>

                                <option value="Hindi">
                                    Hindi
                                </option>

                                <option value="English">
                                    English
                                </option>

                            </select>

                        </div>


                        <div class="admin-form-group admin-form-full">

                            <label>
                                Categories
                            </label>

                            <div
                                id="bookCategories"
                                class="admin-category-list"
                            ></div>

                        </div>


                        <div class="admin-form-group admin-form-full">

                            <label for="bookTags">
                                Tags
                            </label>

                            <input
                                type="text"
                                id="bookTags"
                                placeholder="love, novel, gujarati"
                            >

                        </div>

                    </div>

                </div>


                <div class="admin-form-section">

                    <h3>
                        Images
                    </h3>


                    <div class="admin-form-grid">

                        <div class="admin-form-group">

                            <label for="bookCoverImage">
                                Cover Image
                            </label>

                            <input
                                type="text"
                                id="bookCoverImage"
                                placeholder="/static/uploads/cover.jpg"
                            >

                        </div>


                        <div class="admin-form-group">

                            <label for="bookBannerImage">
                                Banner Image
                            </label>

                            <input
                                type="text"
                                id="bookBannerImage"
                                placeholder="/static/uploads/banner.jpg"
                            >

                        </div>


                        <div class="admin-form-group admin-form-full">

                            <label for="bookFeaturedImage">
                                Featured Image
                            </label>

                            <input
                                type="text"
                                id="bookFeaturedImage"
                                placeholder="/static/uploads/featured.jpg"
                            >

                        </div>

                    </div>

                </div>


                <div class="admin-form-section">

                    <h3>
                        Publishing
                    </h3>


                    <div class="admin-form-grid">

                        <div class="admin-form-group">

                            <label for="bookStatus">
                                Status
                            </label>

                            <select id="bookStatus">

                                <option value="draft">
                                    Draft
                                </option>

                                <option value="published">
                                    Published
                                </option>

                                <option value="private">
                                    Private
                                </option>

                            </select>

                        </div>


                        <div class="admin-form-group">

                            <label for="bookPublishDate">
                                Publish Date
                            </label>

                            <input
                                type="datetime-local"
                                id="bookPublishDate"
                            >

                        </div>


                        <div class="admin-checkbox-row">

                            <label>

                                <input
                                    type="checkbox"
                                    id="bookPublished"
                                >

                                Published

                            </label>


                            <label>

                                <input
                                    type="checkbox"
                                    id="bookFeatured"
                                >

                                Featured

                            </label>

                        </div>

                    </div>

                </div>


                <div class="admin-form-section">

                    <h3>
                        SEO Settings
                    </h3>


                    <div class="admin-form-grid">

                        <div class="admin-form-group admin-form-full">

                            <label for="seoMetaTitle">
                                Meta Title
                            </label>

                            <input
                                type="text"
                                id="seoMetaTitle"
                                maxlength="255"
                            >

                        </div>


                        <div class="admin-form-group admin-form-full">

                            <label for="seoMetaDescription">
                                Meta Description
                            </label>

                            <textarea
                                id="seoMetaDescription"
                                rows="4"
                            ></textarea>

                        </div>


                        <div class="admin-form-group">

                            <label for="seoFocusKeyword">
                                Focus Keyword
                            </label>

                            <input
                                type="text"
                                id="seoFocusKeyword"
                            >

                        </div>


                        <div class="admin-form-group">

                            <label for="seoCanonicalUrl">
                                Canonical URL
                            </label>

                            <input
                                type="text"
                                id="seoCanonicalUrl"
                            >

                        </div>


                        <div class="admin-form-group">

                            <label for="seoRobots">
                                Robots
                            </label>

                            <input
                                type="text"
                                id="seoRobots"
                                value="index, follow"
                            >

                        </div>


                        <div class="admin-form-group">

                            <label for="seoOgTitle">
                                OG Title
                            </label>

                            <input
                                type="text"
                                id="seoOgTitle"
                            >

                        </div>


                        <div class="admin-form-group admin-form-full">

                            <label for="seoOgDescription">
                                OG Description
                            </label>

                            <textarea
                                id="seoOgDescription"
                                rows="3"
                            ></textarea>

                        </div>


                        <div class="admin-form-group">

                            <label for="seoOgImage">
                                OG Image
                            </label>

                            <input
                                type="text"
                                id="seoOgImage"
                            >

                        </div>


                        <div class="admin-form-group admin-form-full">

                            <label for="seoSchemaData">
                                JSON-LD Schema
                            </label>

                            <textarea
                                id="seoSchemaData"
                                rows="8"
                                placeholder='{"@context":"https://schema.org"}'
                            ></textarea>

                        </div>

                    </div>

                </div>


                <div class="admin-modal-footer">

                    <button
                        type="button"
                        class="admin-btn"
                        data-close-book-modal
                    >
                        Cancel
                    </button>


                    <button
                        type="submit"
                        class="admin-btn admin-btn-primary"
                        id="saveBookBtn"
                    >
                        Save Book
                    </button>

                </div>

            </form>

        </div>

        `;


    document.body.appendChild(
        modal
    );


    const form =
        adminBookElement(
            "bookForm"
        );

    if (form) {

        form.addEventListener(
            "submit",
            handleAdminBookSubmit
        );

    }

}


/* =========================================================
   21. OPEN MODAL
========================================================= */

function openAdminBookModal() {

    createAdminBookModalIfMissing();


    AdminBooksState.editingBookId =
        null;


    resetAdminBookForm();


    const title =
        adminBookElement(
            "bookModalTitle"
        );

    if (title) {

        title.textContent =
            "Add Book";

    }


    const modal =
        adminBookElement(
            "bookModal"
        );

    if (!modal) {

        return;

    }


    modal.hidden =
        false;

    document.body.classList.add(
        "admin-modal-open"
    );


    setTimeout(() => {

        adminBookElement(
            "bookTitle"
        )?.focus();

    }, 50);

}


/* =========================================================
   22. CLOSE MODAL
========================================================= */

function closeAdminBookModal() {

    const modal =
        adminBookElement(
            "bookModal"
        );

    if (!modal) {

        return;

    }


    modal.hidden =
        true;

    document.body.classList.remove(
        "admin-modal-open"
    );

}


/* =========================================================
   23. RESET FORM
========================================================= */

function resetAdminBookForm() {

    const form =
        adminBookElement(
            "bookForm"
        );

    if (form) {

        form.reset();

    }


    AdminBooksState.editingBookId =
        null;


    adminBookSetValue(
        "bookStatus",
        "draft"
    );


    adminBookSetChecked(
        "bookPublished",
        false
    );


    adminBookSetChecked(
        "bookFeatured",
        false
    );


    adminBookSetValue(
        "seoRobots",
        "index, follow"
    );


    const categoryContainer =
        adminBookElement(
            "bookCategories"
        );

    if (categoryContainer) {

        categoryContainer
            .querySelectorAll(
                "input[type='checkbox']"
            )
            .forEach(
                checkbox => {

                    checkbox.checked =
                        false;

                }
            );

    }

}


/* =========================================================
   24. EDIT BOOK
========================================================= */

async function editAdminBook(
    bookId
) {

    if (!bookId) {

        return;

    }


    try {

        setAdminBookLoading(true);


        const data =
            await adminBooksRequest(
                `/api/admin/books/${bookId}`
            );


        const book =
            data.book;


        if (!book) {

            throw new Error(
                "Book data not found."
            );

        }


        AdminBooksState.editingBookId =
            book.id;


        createAdminBookModalIfMissing();


        fillAdminBookForm(
            book
        );


        const title =
            adminBookElement(
                "bookModalTitle"
            );

        if (title) {

            title.textContent =
                "Edit Book";

        }


        const modal =
            adminBookElement(
                "bookModal"
            );

        if (modal) {

            modal.hidden =
                false;

        }


        document.body.classList.add(
            "admin-modal-open"
        );


    } catch (error) {

        console.error(error);

        showAdminBookToast(
            error.message ||
            "Unable to load book.",
            "error"
        );

    } finally {

        setAdminBookLoading(false);

    }

}


/* =========================================================
   25. FILL BOOK FORM
========================================================= */

function fillAdminBookForm(
    book
) {

    adminBookSetValue(
        "bookTitle",
        book.title
    );


    adminBookSetValue(
        "bookSlug",
        book.slug
    );


    adminBookSetValue(
        "bookSubtitle",
        book.subtitle
    );


    adminBookSetValue(
        "bookShortDescription",
        book.short_description
    );


    adminBookSetValue(
        "bookDescription",
        book.description
    );


    adminBookSetValue(
        "bookAuthor",
        book.author_id
    );


    adminBookSetValue(
        "bookLanguage",
        book.language
    );


    adminBookSetValue(
        "bookTags",
        book.tags
    );


    adminBookSetValue(
        "bookCoverImage",
        book.cover_image
    );


    adminBookSetValue(
        "bookBannerImage",
        book.banner_image
    );


    adminBookSetValue(
        "bookFeaturedImage",
        book.featured_image
    );


    adminBookSetValue(
        "bookStatus",
        book.status || "draft"
    );


    adminBookSetChecked(
        "bookPublished",
        Boolean(book.published)
    );


    adminBookSetChecked(
        "bookFeatured",
        Boolean(book.featured)
    );


    adminBookSetValue(
        "bookPublishDate",
        formatDateTimeLocal(
            book.publish_date
        )
    );


    fillAdminBookCategories(
        book.category_ids ||
        []
    );


    const seo =
        book.seo || {};


    adminBookSetValue(
        "seoMetaTitle",
        seo.meta_title
    );


    adminBookSetValue(
        "seoMetaDescription",
        seo.meta_description
    );


    adminBookSetValue(
        "seoFocusKeyword",
        seo.focus_keyword
    );


    adminBookSetValue(
        "seoCanonicalUrl",
        seo.canonical_url
    );


    adminBookSetValue(
        "seoRobots",
        seo.robots ||
        "index, follow"
    );


    adminBookSetValue(
        "seoOgTitle",
        seo.og_title
    );


    adminBookSetValue(
        "seoOgDescription",
        seo.og_description
    );


    adminBookSetValue(
        "seoOgImage",
        seo.og_image
    );


    adminBookSetValue(
        "seoSchemaData",
        seo.schema_data
    );

}


/* =========================================================
   26. FILL CATEGORIES
========================================================= */

function fillAdminBookCategories(
    categoryIds
) {

    const ids =
        new Set(
            (Array.isArray(categoryIds)
                ? categoryIds
                : []
            ).map(
                id => String(id)
            )
        );


    const container =
        adminBookElement(
            "bookCategories"
        );

    if (!container) {

        return;

    }


    container
        .querySelectorAll(
            "input[type='checkbox']"
        )
        .forEach(
            checkbox => {

                checkbox.checked =
                    ids.has(
                        String(
                            checkbox.value
                        )
                    );

            }
        );

}


/* =========================================================
   27. FORMAT DATETIME
========================================================= */

function formatDateTimeLocal(
    value
) {

    if (!value) {

        return "";

    }


    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return "";

    }


    const year =
        date.getFullYear();


    const month =
        String(
            date.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const day =
        String(
            date.getDate()
        ).padStart(
            2,
            "0"
        );


    const hours =
        String(
            date.getHours()
        ).padStart(
            2,
            "0"
        );


    const minutes =
        String(
            date.getMinutes()
        ).padStart(
            2,
            "0"
        );


    return (
        `${year}-${month}-${day}` +
        `T${hours}:${minutes}`
    );

}


/* =========================================================
   28. COLLECT CATEGORY IDS
========================================================= */

function collectAdminBookCategoryIds() {

    const container =
        adminBookElement(
            "bookCategories"
        );

    if (!container) {

        return [];

    }


    return Array.from(
        container.querySelectorAll(
            "input[type='checkbox']:checked"
        )
    )
    .map(
        checkbox =>
            Number(
                checkbox.value
            )
    )
    .filter(
        id =>
            Number.isInteger(id) &&
            id > 0
    );

}


/* =========================================================
   29. COLLECT FORM DATA
========================================================= */

function collectAdminBookFormData() {

    return {

        title:
            adminBookValue(
                "bookTitle"
            ).trim(),

        slug:
            adminBookValue(
                "bookSlug"
            ).trim(),

        subtitle:
            adminBookValue(
                "bookSubtitle"
            ).trim(),

        short_description:
            adminBookValue(
                "bookShortDescription"
            ).trim(),

        description:
            adminBookValue(
                "bookDescription"
            ).trim(),

        author_id:
            adminBookValue(
                "bookAuthor"
            )
                ? Number(
                    adminBookValue(
                        "bookAuthor"
                    )
                )
                : null,

        language:
            adminBookValue(
                "bookLanguage"
            ).trim(),

        tags:
            adminBookValue(
                "bookTags"
            ).trim(),

        cover_image:
            adminBookValue(
                "bookCoverImage"
            ).trim(),

        banner_image:
            adminBookValue(
                "bookBannerImage"
            ).trim(),

        featured_image:
            adminBookValue(
                "bookFeaturedImage"
            ).trim(),

        status:
            adminBookValue(
                "bookStatus"
            ) || "draft",

        published:
            adminBookChecked(
                "bookPublished"
            ),

        featured:
            adminBookChecked(
                "bookFeatured"
            ),

        publish_date:
            adminBookValue(
                "bookPublishDate"
            ) || null,

        category_ids:
            collectAdminBookCategoryIds(),

        meta_title:
            adminBookValue(
                "seoMetaTitle"
            ).trim(),

        meta_description:
            adminBookValue(
                "seoMetaDescription"
            ).trim(),

        focus_keyword:
            adminBookValue(
                "seoFocusKeyword"
            ).trim(),

        canonical_url:
            adminBookValue(
                "seoCanonicalUrl"
            ).trim(),

        robots:
            adminBookValue(
                "seoRobots"
            ).trim(),

        og_title:
            adminBookValue(
                "seoOgTitle"
            ).trim(),

        og_description:
            adminBookValue(
                "seoOgDescription"
            ).trim(),

        og_image:
            adminBookValue(
                "seoOgImage"
            ).trim(),

        schema_data:
            adminBookValue(
                "seoSchemaData"
            ).trim()

    };

}


/* =========================================================
   30. VALIDATE FORM
========================================================= */

function validateAdminBookForm(
    data
) {

    if (!data.title) {

        return "Book title is required.";

    }


    if (!data.slug) {

        return "Book slug is required.";

    }


    if (
        !/^[a-z0-9]+(?:-[a-z0-9]+)*$/i.test(
            data.slug
        )
    ) {

        return (
            "Slug can contain only letters, " +
            "numbers and hyphens."
        );

    }


    if (
        data.author_id !== null &&
        (
            !Number.isInteger(
                data.author_id
            ) ||
            data.author_id <= 0
        )
    ) {

        return "Please select a valid author.";

    }


    if (
        data.publish_date &&
        Number.isNaN(
            new Date(
                data.publish_date
            ).getTime()
        )
    ) {

        return "Invalid publish date.";

    }


    if (
        data.schema_data
    ) {

        try {

            JSON.parse(
                data.schema_data
            );

        } catch (error) {

            return (
                "JSON-LD Schema contains invalid JSON."
            );

        }

    }


    return null;

}


/* =========================================================
   31. SUBMIT BOOK
========================================================= */

async function handleAdminBookSubmit(
    event
) {

    event.preventDefault();


    const data =
        collectAdminBookFormData();


    const validationError =
        validateAdminBookForm(
            data
        );


    if (validationError) {

        showAdminBookToast(
            validationError,
            "error"
        );

        return;

    }


    const saveButton =
        adminBookElement(
            "saveBookBtn"
        );


    if (saveButton) {

        saveButton.disabled =
            true;

        saveButton.dataset.originalText =
            saveButton.textContent;

        saveButton.textContent =
            "Saving...";

    }


    try {

        /*
         * IMPORTANT:
         * Backend save_book_seo() expects SEO
         * fields at the top level.
         *
         * Therefore we intentionally send:
         *
         * meta_title
         * meta_description
         * focus_keyword
         * canonical_url
         * robots
         * og_title
         * og_description
         * og_image
         * schema_data
         *
         * instead of seo: {...}
         */


        let url =
            "/api/admin/books";


        let method =
            "POST";


        if (
            AdminBooksState.editingBookId
        ) {

            url =
                `/api/admin/books/` +
                AdminBooksState.editingBookId;

            method =
                "PUT";

        }


        const response =
            await adminBooksRequest(
                url,
                {

                    method,

                    body:
                        JSON.stringify(
                            data
                        )

                }
            );


        showAdminBookToast(

            response.message ||
            (
                AdminBooksState.editingBookId
                    ? "Book updated successfully."
                    : "Book created successfully."
            ),

            "success"

        );


        closeAdminBookModal();


        await loadAdminBooks();


    } catch (error) {

        console.error(error);

        showAdminBookToast(
            error.message ||
            "Unable to save book.",
            "error"
        );

    } finally {

        if (saveButton) {

            saveButton.disabled =
                false;

            saveButton.textContent =
                saveButton.dataset.originalText ||
                "Save Book";

        }

    }

}


/* =========================================================
   32. DELETE BOOK
========================================================= */

function deleteAdminBook(
    bookId
) {

    if (!bookId) {

        return;

    }


    const book =
        AdminBooksState.books.find(
            item =>
                Number(item.id) ===
                Number(bookId)
        );


    AdminBooksState.deletingBookId =
        Number(bookId);


    createAdminBookConfirmModalIfMissing();


    const message =
        adminBookElement(
            "bookDeleteMessage"
        );


    if (message) {

        message.textContent =
            book
                ? `Delete "${book.title}"? This action cannot be undone.`
                : "Delete this book? This action cannot be undone.";

    }


    const modal =
        adminBookElement(
            "bookConfirmModal"
        );


    if (modal) {

        modal.hidden =
            false;

    }


    document.body.classList.add(
        "admin-modal-open"
    );

}


/* =========================================================
   33. CREATE CONFIRM MODAL
========================================================= */

function createAdminBookConfirmModalIfMissing() {

    if (
        adminBookElement(
            "bookConfirmModal"
        )
    ) {

        return;

    }


    const modal =
        document.createElement(
            "div"
        );

    modal.id =
        "bookConfirmModal";

    modal.className =
        "admin-modal-overlay";

    modal.hidden =
        true;


    modal.innerHTML =
        `

        <div
            class="admin-modal admin-confirm-modal"
            role="dialog"
            aria-modal="true"
        >

            <div class="admin-modal-header">

                <div>

                    <h2>
                        Delete Book
                    </h2>

                </div>

                <button
                    type="button"
                    class="admin-modal-close"
                    data-cancel-book-delete
                    aria-label="Close"
                >
                    ×
                </button>

            </div>


            <div class="admin-confirm-content">

                <p id="bookDeleteMessage">
                    Delete this book?
                </p>

            </div>


            <div class="admin-modal-footer">

                <button
                    type="button"
                    class="admin-btn"
                    data-cancel-book-delete
                >
                    Cancel
                </button>


                <button
                    type="button"
                    class="admin-btn admin-btn-danger"
                    data-confirm-book-delete
                >
                    Delete
                </button>

            </div>

        </div>

        `;


    document.body.appendChild(
        modal
    );

}


/* =========================================================
   34. CONFIRM DELETE
========================================================= */

async function confirmAdminBookDelete() {

    const bookId =
        AdminBooksState.deletingBookId;


    if (!bookId) {

        return;

    }


    try {

        const response =
            await adminBooksRequest(
                `/api/admin/books/${bookId}`,
                {

                    method:
                        "DELETE"

                }
            );


        showAdminBookToast(

            response.message ||
            "Book deleted successfully.",

            "success"

        );


        closeAdminBookConfirm();


        await loadAdminBooks();


    } catch (error) {

        console.error(error);

        showAdminBookToast(
            error.message ||
            "Unable to delete book.",
            "error"
        );

    }

}


/* =========================================================
   35. CLOSE CONFIRM MODAL
========================================================= */

function closeAdminBookConfirm() {

    const modal =
        adminBookElement(
            "bookConfirmModal"
        );

    if (modal) {

        modal.hidden =
            true;

    }


    AdminBooksState.deletingBookId =
        null;


    document.body.classList.remove(
        "admin-modal-open"
    );

}


/* =========================================================
   36. TOGGLE PUBLISHED
========================================================= */

async function toggleAdminBookPublished(
    bookId
) {

    const book =
        AdminBooksState.books.find(
            item =>
                Number(item.id) ===
                Number(bookId)
        );


    if (!book) {

        return;

    }


    const newValue =
        !Boolean(
            book.published
        );


    try {

        await adminBooksRequest(

            `/api/admin/books/${bookId}`,

            {

                method:
                    "PATCH",

                body:
                    JSON.stringify({

                        published:
                            newValue

                    })

            }

        );


        showAdminBookToast(

            newValue
                ? "Book published."
                : "Book unpublished.",

            "success"

        );


        await loadAdminBooks();


    } catch (error) {

        console.error(error);

        showAdminBookToast(
            error.message ||
            "Unable to change publish status.",
            "error"
        );

    }

}


/* =========================================================
   37. TOGGLE FEATURED
========================================================= */

async function toggleAdminBookFeatured(
    bookId
) {

    const book =
        AdminBooksState.books.find(
            item =>
                Number(item.id) ===
                Number(bookId)
        );


    if (!book) {

        return;

    }


    const newValue =
        !Boolean(
            book.featured
        );


    try {

        await adminBooksRequest(

            `/api/admin/books/${bookId}`,

            {

                method:
                    "PATCH",

                body:
                    JSON.stringify({

                        featured:
                            newValue

                    })

            }

        );


        showAdminBookToast(

            newValue
                ? "Book marked as featured."
                : "Book removed from featured.",

            "success"

        );


        await loadAdminBooks();


    } catch (error) {

        console.error(error);

        showAdminBookToast(
            error.message ||
            "Unable to change featured status.",
            "error"
        );

    }

}


/* =========================================================
   38. AUTO SLUG
========================================================= */

const adminBookTitleObserver =
    document;


document.addEventListener(
    "input",
    event => {

        if (
            event.target?.id !==
            "bookTitle"
        ) {

            return;

        }


        const slug =
            adminBookElement(
                "bookSlug"
            );


        if (!slug) {

            return;

        }


        if (
            AdminBooksState.editingBookId
        ) {

            return;

        }


        slug.value =
            generateAdminBookSlug(
                event.target.value
            );

    }
);


/* =========================================================
   39. SLUG GENERATOR
========================================================= */

function generateAdminBookSlug(
    value
) {

    return String(
        value || ""
    )

        .toLowerCase()

        .trim()

        .replace(
            /[^\p{L}\p{N}\s-]/gu,
            ""
        )

        .replace(
            /\s+/g,
            "-"
        )

        .replace(
            /-+/g,
            "-"
        )

        .replace(
            /^-|-$/g,
            ""
        );

}


/* =========================================================
   40. SEO AUTO DEFAULTS
========================================================= */

document.addEventListener(
    "input",
    event => {

        if (
            event.target?.id !==
            "bookTitle"
        ) {

            return;

        }


        if (
            AdminBooksState.editingBookId
        ) {

            return;

        }


        const title =
            event.target.value.trim();


        if (!title) {

            return;

        }


        const metaTitle =
            adminBookElement(
                "seoMetaTitle"
            );


        const focusKeyword =
            adminBookElement(
                "seoFocusKeyword"
            );


        if (
            metaTitle &&
            !metaTitle.value.trim()
        ) {

            metaTitle.value =
                `${title} | Rasbhav Books`;

        }


        if (
            focusKeyword &&
            !focusKeyword.value.trim()
        ) {

            focusKeyword.value =
                title;

        }

    }
);


/* =========================================================
   41. DESCRIPTION SEO DEFAULT
========================================================= */

document.addEventListener(
    "input",
    event => {

        if (
            event.target?.id !==
            "bookShortDescription"
        ) {

            return;

        }


        if (
            AdminBooksState.editingBookId
        ) {

            return;

        }


        const description =
            event.target.value.trim();


        const metaDescription =
            adminBookElement(
                "seoMetaDescription"
            );


        if (
            metaDescription &&
            !metaDescription.value.trim()
        ) {

            metaDescription.value =
                description;

        }


        const ogDescription =
            adminBookElement(
                "seoOgDescription"
            );


        if (
            ogDescription &&
            !ogDescription.value.trim()
        ) {

            ogDescription.value =
                description;

        }

    }
);


/* =========================================================
   42. STATUS / PUBLISHED SYNC
========================================================= */

document.addEventListener(
    "change",
    event => {

        if (
            event.target?.id !==
            "bookStatus"
        ) {

            return;

        }


        const status =
            event.target.value;


        const published =
            adminBookElement(
                "bookPublished"
            );


        if (!published) {

            return;

        }


        if (
            status === "published"
        ) {

            published.checked =
                true;

        }

        if (
            status === "draft" ||
            status === "private"
        ) {

            published.checked =
                false;

        }

    }
);


/* =========================================================
   43. PUBLISHED / STATUS SYNC
========================================================= */

document.addEventListener(
    "change",
    event => {

        if (
            event.target?.id !==
            "bookPublished"
        ) {

            return;

        }


        const status =
            adminBookElement(
                "bookStatus"
            );


        if (!status) {

            return;

        }


        status.value =
            event.target.checked
                ? "published"
                : "draft";

    }
);


/* =========================================================
   44. GLOBAL PUBLIC API
========================================================= */

window.RasbhavAdminBooks = {

    load:
        loadAdminBooks,

    add:
        openAdminBookModal,

    edit:
        editAdminBook,

    delete:
        deleteAdminBook,

    publish:
        toggleAdminBookPublished,

    featured:
        toggleAdminBookFeatured

};


/* =========================================================
   END
========================================================= */
