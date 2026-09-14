/* =========================================================
   RASBHAV BOOKS
   ADMIN BOOKS CMS JAVASCRIPT

   File:
   app/static/js/admin-books.js

   Backend:
   /api/admin/books
   /api/admin/authors
   /api/admin/categories

   Features:
   - Load books
   - Search
   - Filter
   - Create book
   - Edit book
   - Delete book
   - Publish / Unpublish
   - Featured / Unfeatured
   - Author loading
   - Category loading
   - SEO data
   - Form validation
   - Toast messages
   - Modal control
   - Safe API handling

   IMPORTANT:
   No CSS is written here.
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

    loading: false,

    searchTimer: null,

    initialized: false

};


/* =========================================================
   2. API HELPERS
========================================================= */

async function adminBooksRequest(
    url,
    options = {}
) {

    const config = {
        credentials: "same-origin",

        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },

        ...options
    };

    try {

        const response = await fetch(
            url,
            config
        );

        let data = null;

        const contentType =
            response.headers.get(
                "content-type"
            ) || "";

        if (
            contentType.includes(
                "application/json"
            )
        ) {

            data = await response.json();

        } else {

            const text =
                await response.text();

            data = {
                success:
                    response.ok,

                message:
                    text || "Unknown server response."
            };
        }

        if (!response.ok) {

            throw new Error(
                data.message ||
                data.error ||
                "Request failed."
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


function adminBookSetValue(
    id,
    value
) {

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


function adminBookSetChecked(
    id,
    value
) {

    const element =
        adminBookElement(id);

    if (!element) {
        return;
    }

    element.checked =
        Boolean(value);

}


/* =========================================================
   4. TOAST
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
            document.createElement(
                "div"
            );

        container.className =
            "admin-toast-container";

        document.body.appendChild(
            container
        );
    }

    const toast =
        document.createElement(
            "div"
        );

    toast.className =
        `admin-toast ${type}`;

    toast.textContent =
        message;

    container.appendChild(
        toast
    );

    setTimeout(() => {

        toast.style.opacity =
            "0";

        toast.style.transform =
            "translateY(8px)";

        setTimeout(() => {

            toast.remove();

        }, 200);

    }, 3000);
}


/* =========================================================
   5. ESCAPE HTML
========================================================= */

function escapeAdminBookHTML(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


/* =========================================================
   6. INITIALIZE
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
   7. INITIALIZE ADMIN BOOKS
========================================================= */

async function initializeAdminBooks() {

    bindAdminBookEvents();

    createAdminBookModalIfMissing();

    setAdminBookLoading(
        true
    );

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

        setAdminBookLoading(
            false
        );
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
            () => {

                openAdminBookModal();

            }
        );
    }


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


    const closeButton =
        adminBookElement(
            "closeBookModal"
        );

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeAdminBookModal
        );
    }


    const cancelButton =
        adminBookElement(
            "cancelBookBtn"
        );

    if (cancelButton) {

        cancelButton.addEventListener(
            "click",
            closeAdminBookModal
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
   9. DOCUMENT CLICK
========================================================= */

function handleAdminBookDocumentClick(
    event
) {

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


    const overlay =
        event.target.closest(
            ".admin-modal-overlay"
        );

    if (
        overlay &&
        event.target === overlay
    ) {

        closeAdminBookModal();

        closeAdminBookConfirm();
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

    setAdminBookLoading(
        true
    );

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


        const query =
            params.toString();

        const url =
            query
                ? `/api/admin/books?${query}`
                : "/api/admin/books";


        const data =
            await adminBooksRequest(
                url
            );


        const books =
            Array.isArray(
                data.books
            )
                ? data.books
                : Array.isArray(
                    data.results
                )
                    ? data.results
                    : Array.isArray(
                        data.data
                    )
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

        renderAdminBooksError(
            error.message
        );

    } finally {

        AdminBooksState.loading =
            false;

        setAdminBookLoading(
            false
        );
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
            Array.isArray(
                data.authors
            )
                ? data.authors
                : Array.isArray(
                    data.results
                )
                    ? data.results
                    : Array.isArray(
                        data.data
                    )
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
            Array.isArray(
                data.categories
            )
                ? data.categories
                : Array.isArray(
                    data.results
                )
                    ? data.results
                    : Array.isArray(
                        data.data
                    )
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
                "admin-checkbox-row";


            const checkbox =
                document.createElement(
                    "input"
                );

            checkbox.type =
                "checkbox";

            checkbox.className =
                "admin-checkbox";

            checkbox.name =
                "book_category";

            checkbox.value =
                category.id;


            const text =
                document.createElement(
                    "span"
                );

            text.className =
                "admin-checkbox-label";

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
        !books ||
        books.length === 0
    ) {

        tbody.innerHTML =
            `
            <tr>
                <td colspan="100%">
                    <div class="admin-empty">
                        <div class="admin-empty-icon">
                            📚
                        </div>

                        <h3 class="admin-empty-title">
                            No books found
                        </h3>

                        <p class="admin-empty-text">
                            Add a new book or change your search/filter.
                        </p>
                    </div>
                </td>
            </tr>
            `;

        return;
    }


    tbody.innerHTML =
        books.map(
            book =>
                renderAdminBookRow(
                    book
                )
        ).join("");
}


/* =========================================================
   16. BOOK ROW
========================================================= */

function renderAdminBookRow(
    book
) {

    const title =
        escapeAdminBookHTML(
            book.title
        );


    const slug =
        escapeAdminBookHTML(
            book.slug
        );


    const author =
        escapeAdminBookHTML(
            book.author?.name ||
            "No Author"
        );


    const language =
        escapeAdminBookHTML(
            book.language ||
            "-"
        );


    const cover =
        book.cover_image
            ? `
                <img
                    src="${escapeAdminBookHTML(
                        book.cover_image
                    )}"
                    alt="${title}"
                    class="admin-book-cover"
                    loading="lazy"
                    onerror="this.style.display='none';"
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
        escapeAdminBookHTML(
            book.status ||
            "draft"
        );


    const publishBadge =
        published
            ? `
                <span class="admin-badge admin-badge-success">
                    Published
                </span>
              `
            : `
                <span class="admin-badge admin-badge-warning">
                    Draft
                </span>
              `;


    const featuredBadge =
        featured
            ? `
                <span class="admin-badge admin-badge-gold">
                    Featured
                </span>
              `
            : `
                <span class="admin-badge admin-badge-neutral">
                    Normal
                </span>
              `;


    const publishText =
        published
            ? "Unpublish"
            : "Publish";


    return `
        <tr>

            <td>
                <div class="admin-book-cell">

                    ${cover}

                    <div class="admin-book-info">

                        <div
                            class="admin-book-title"
                            title="${title}"
                        >
                            ${title}
                        </div>

                        <div
                            class="admin-book-slug"
                            title="${slug}"
                        >
                            /books/${slug}
                        </div>

                    </div>

                </div>
            </td>


            <td>
                ${author}
            </td>


            <td>
                ${language}
            </td>


            <td>
                ${publishBadge}
            </td>


            <td>
                ${featuredBadge}
            </td>


            <td>
                <span class="admin-badge admin-badge-neutral">
                    ${status}
                </span>
            </td>


            <td>

                <div class="admin-table-actions">

                    <button
                        type="button"
                        class="admin-btn admin-btn-secondary admin-btn-sm"
                        data-book-edit="${book.id}"
                    >
                        Edit
                    </button>


                    <button
                        type="button"
                        class="admin-btn admin-btn-info admin-btn-sm"
                        data-book-publish="${book.id}"
                    >
                        ${publishText}
                    </button>


                    <button
                        type="button"
                        class="admin-btn admin-btn-secondary admin-btn-sm"
                        data-book-featured="${book.id}"
                    >
                        ${featured
                            ? "Unfeature"
                            : "Feature"}
                    </button>


                    <button
                        type="button"
                        class="admin-btn admin-btn-danger admin-btn-sm"
                        data-book-delete="${book.id}"
                    >
                        Delete
                    </button>

                </div>

            </td>

        </tr>
    `;
}


/* =========================================================
   17. UPDATE COUNT
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
}


/* =========================================================
   18. OPEN NEW BOOK
========================================================= */

function openAdminBookModal() {

    AdminBooksState.editingBookId =
        null;


    resetAdminBookForm();


    const title =
        adminBookElement(
            "bookModalTitle"
        );

    if (title) {

        title.textContent =
            "Add New Book";
    }


    const saveButton =
        adminBookElement(
            "saveBookBtn"
        );

    if (saveButton) {

        saveButton.textContent =
            "Create Book";
    }


    openAdminBookModalElement();

}


/* =========================================================
   19. EDIT BOOK
========================================================= */

async function editAdminBook(
    bookId
) {

    if (!bookId) {

        return;
    }


    try {

        const data =
            await adminBooksRequest(
                `/api/admin/books/${bookId}`
            );


        const book =
            data.book ||
            data.data ||
            data;


        if (!book) {

            throw new Error(
                "Book data not found."
            );
        }


        AdminBooksState.editingBookId =
            book.id;


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


        const saveButton =
            adminBookElement(
                "saveBookBtn"
            );

        if (saveButton) {

            saveButton.textContent =
                "Update Book";
        }


        openAdminBookModalElement();


    } catch (error) {

        showAdminBookToast(
            error.message ||
            "Could not load book.",
            "error"
        );
    }
}


/* =========================================================
   20. FILL BOOK FORM
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
        book.published
    );

    adminBookSetChecked(
        "bookFeatured",
        book.featured
    );


    const authorSelect =
        adminBookElement(
            "bookAuthor"
        );

    if (authorSelect) {

        authorSelect.value =
            book.author_id ||
            book.author?.id ||
            "";
    }


    clearAdminBookCategories();


    const categoryIds =
        Array.isArray(
            book.category_ids
        )
            ? book.category_ids
            : Array.isArray(
                book.categories
            )
                ? book.categories.map(
                    category =>
                        category.id
                )
                : [];


    categoryIds.forEach(
        id => {

            const checkbox =
                document.querySelector(
                    `input[name="book_category"][value="${id}"]`
                );

            if (checkbox) {

                checkbox.checked =
                    true;
            }
        }
    );


    const seo =
        book.seo ||
        {};


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
   21. RESET FORM
========================================================= */

function resetAdminBookForm() {

    const form =
        adminBookElement(
            "bookForm"
        );

    if (form) {

        form.reset();
    }


    adminBookSetValue(
        "bookStatus",
        "draft"
    );


    adminBookSetValue(
        "seoRobots",
        "index, follow"
    );


    clearAdminBookCategories();


    AdminBooksState.editingBookId =
        null;
}


/* =========================================================
   22. CLEAR CATEGORIES
========================================================= */

function clearAdminBookCategories() {

    const checkboxes =
        document.querySelectorAll(
            'input[name="book_category"]'
        );


    checkboxes.forEach(
        checkbox => {

            checkbox.checked =
                false;
        }
    );
}


/* =========================================================
   23. COLLECT CATEGORY IDS
========================================================= */

function collectAdminBookCategoryIds() {

    const checkboxes =
        document.querySelectorAll(
            'input[name="book_category"]:checked'
        );


    return Array.from(
        checkboxes
    ).map(
        checkbox =>
            Number(
                checkbox.value
            )
    ).filter(
        Number.isFinite
    );
}


/* =========================================================
   24. COLLECT FORM DATA
========================================================= */

function collectAdminBookFormData() {

    const categoryIds =
        collectAdminBookCategoryIds();


    const data = {

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

        category_ids:
            categoryIds,

        seo: {

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
        }
    };


    return data;
}


/* =========================================================
   25. VALIDATE FORM
========================================================= */

function validateAdminBookForm(
    data
) {

    if (!data.title) {

        return "Book title is required.";
    }


    if (
        data.title.length < 2
    ) {

        return "Book title is too short.";
    }


    if (
        data.slug &&
        !/^[a-z0-9]+(?:-[a-z0-9]+)*$/i.test(
            data.slug
        )
    ) {

        return (
            "Slug may contain only letters, " +
            "numbers and hyphens."
        );
    }


    if (
        data.author_id !== null &&
        !Number.isInteger(
            data.author_id
        )
    ) {

        return "Invalid author.";
    }


    if (
        data.seo.schema_data
    ) {

        try {

            JSON.parse(
                data.seo.schema_data
            );

        } catch (
            error
        ) {

            return (
                "SEO Schema JSON is invalid."
            );
        }
    }


    return null;
}


/* =========================================================
   26. SUBMIT BOOK
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


    const editingId =
        AdminBooksState.editingBookId;


    const isEditing =
        Boolean(
            editingId
        );


    const button =
        adminBookElement(
            "saveBookBtn"
        );


    if (button) {

        button.disabled =
            true;

        button.textContent =
            isEditing
                ? "Updating..."
                : "Creating...";
    }


    try {

        const url =
            isEditing
                ? `/api/admin/books/${editingId}`
                : "/api/admin/books";


        const method =
            isEditing
                ? "PUT"
                : "POST";


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
                isEditing
                    ? "Book updated successfully."
                    : "Book created successfully."
            ),
            "success"
        );


        closeAdminBookModal();


        await loadAdminBooks();


    } catch (error) {

        showAdminBookToast(
            error.message ||
            "Could not save book.",
            "error"
        );

    } finally {

        if (button) {

            button.disabled =
                false;

            button.textContent =
                isEditing
                    ? "Update Book"
                    : "Create Book";
        }
    }
}


/* =========================================================
   27. DELETE BOOK
========================================================= */

async function deleteAdminBook(
    bookId
) {

    const book =
        AdminBooksState.books.find(
            item =>
                Number(item.id) ===
                Number(bookId)
        );


    const title =
        book?.title ||
        "this book";


    const confirmed =
        await showAdminBookConfirm(
            "Delete Book?",
            `Are you sure you want to delete "${title}"? This action cannot be undone.`
        );


    if (!confirmed) {

        return;
    }


    try {

        const response =
            await adminBooksRequest(
                `/api/admin/books/${bookId}`,
                {
                    method: "DELETE"
                }
            );


        showAdminBookToast(
            response.message ||
            "Book deleted successfully.",
            "success"
        );


        await loadAdminBooks();


    } catch (error) {

        showAdminBookToast(
            error.message ||
            "Could not delete book.",
            "error"
        );
    }
}


/* =========================================================
   28. TOGGLE PUBLISHED
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


    const nextValue =
        !Boolean(
            book.published
        );


    try {

        const response =
            await adminBooksRequest(
                `/api/admin/books/${bookId}`,
                {
                    method: "PATCH",

                    body:
                        JSON.stringify({
                            published:
                                nextValue,

                            status:
                                nextValue
                                    ? "published"
                                    : "draft"
                        })
                }
            );


        showAdminBookToast(
            response.message ||
            (
                nextValue
                    ? "Book published."
                    : "Book unpublished."
            ),
            "success"
        );


        await loadAdminBooks();


    } catch (error) {

        showAdminBookToast(
            error.message ||
            "Could not change publish status.",
            "error"
        );
    }
}


/* =========================================================
   29. TOGGLE FEATURED
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


    const nextValue =
        !Boolean(
            book.featured
        );


    try {

        const response =
            await adminBooksRequest(
                `/api/admin/books/${bookId}`,
                {
                    method: "PATCH",

                    body:
                        JSON.stringify({
                            featured:
                                nextValue
                        })
                }
            );


        showAdminBookToast(
            response.message ||
            (
                nextValue
                    ? "Book marked as featured."
                    : "Book removed from featured."
            ),
            "success"
        );


        await loadAdminBooks();


    } catch (error) {

        showAdminBookToast(
            error.message ||
            "Could not change featured status.",
            "error"
        );
    }
}


/* =========================================================
   30. LOADING STATE
========================================================= */

function setAdminBookLoading(
    loading
) {

    const loadingElement =
        adminBookElement(
            "booksLoading"
        );


    if (loadingElement) {

        loadingElement.classList.toggle(
            "admin-hidden",
            !loading
        );
    }
}


/* =========================================================
   31. ERROR STATE
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

            <td colspan="100%">

                <div class="admin-empty">

                    <div class="admin-empty-icon">
                        ⚠️
                    </div>

                    <h3 class="admin-empty-title">
                        Could not load books
                    </h3>

                    <p class="admin-empty-text">
                        ${escapeAdminBookHTML(
                            message ||
                            "Unknown error."
                        )}
                    </p>

                    <button
                        type="button"
                        class="admin-btn admin-btn-primary admin-btn-sm"
                        onclick="loadAdminBooks()"
                    >
                        Try Again
                    </button>

                </div>

            </td>

        </tr>
        `;
}


/* =========================================================
   32. CREATE MODAL IF MISSING
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


    modal.innerHTML =
        `
        <div
            class="admin-modal admin-modal-lg"
            role="dialog"
            aria-modal="true"
        >

            <div class="admin-modal-header">

                <div>

                    <h2
                        id="bookModalTitle"
                        class="admin-modal-title"
                    >
                        Add New Book
                    </h2>

                </div>


                <button
                    type="button"
                    id="closeBookModal"
                    class="admin-modal-close"
                    aria-label="Close"
                >
                    ×
                </button>

            </div>


            <div class="admin-modal-body">

                <form
                    id="bookForm"
                    class="admin-book-editor"
                >

                    <!-- =================================
                         BASIC INFORMATION
                    ================================== -->

                    <section
                        class="admin-editor-section"
                    >

                        <h3
                            class="admin-editor-section-title"
                        >
                            Basic Information
                        </h3>


                        <div
                            class="admin-form-grid"
                        >

                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="bookTitle"
                                >
                                    Book Title
                                    <span class="admin-required">
                                        *
                                    </span>
                                </label>

                                <input
                                    type="text"
                                    id="bookTitle"
                                    class="admin-input"
                                    required
                                    placeholder="Enter book title"
                                >

                            </div>


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="bookSlug"
                                >
                                    Slug
                                </label>

                                <input
                                    type="text"
                                    id="bookSlug"
                                    class="admin-input"
                                    placeholder="book-slug"
                                >

                            </div>


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="bookLanguage"
                                >
                                    Language
                                </label>

                                <select
                                    id="bookLanguage"
                                    class="admin-select"
                                >

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


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="bookAuthor"
                                >
                                    Author
                                </label>

                                <select
                                    id="bookAuthor"
                                    class="admin-select"
                                >

                                    <option value="">
                                        Select Author
                                    </option>

                                </select>

                            </div>


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="bookStatus"
                                >
                                    Status
                                </label>

                                <select
                                    id="bookStatus"
                                    class="admin-select"
                                >

                                    <option value="draft">
                                        Draft
                                    </option>

                                    <option value="published">
                                        Published
                                    </option>

                                    <option value="archived">
                                        Archived
                                    </option>

                                </select>

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="bookSubtitle"
                                >
                                    Subtitle
                                </label>

                                <input
                                    type="text"
                                    id="bookSubtitle"
                                    class="admin-input"
                                    placeholder="Book subtitle"
                                >

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="bookShortDescription"
                                >
                                    Short Description
                                </label>

                                <textarea
                                    id="bookShortDescription"
                                    class="admin-textarea"
                                    placeholder="Short description"
                                ></textarea>

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="bookDescription"
                                >
                                    Full Description
                                </label>

                                <textarea
                                    id="bookDescription"
                                    class="admin-textarea"
                                    style="min-height:180px;"
                                    placeholder="Full book description"
                                ></textarea>

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="bookTags"
                                >
                                    Tags
                                </label>

                                <input
                                    type="text"
                                    id="bookTags"
                                    class="admin-input"
                                    placeholder="love, novel, gujarati"
                                >

                            </div>

                        </div>

                    </section>


                    <!-- =================================
                         CATEGORIES
                    ================================== -->

                    <section
                        class="admin-editor-section"
                    >

                        <h3
                            class="admin-editor-section-title"
                        >
                            Categories
                        </h3>


                        <div
                            id="bookCategories"
                            class="admin-form-grid"
                        >
                        </div>

                    </section>


                    <!-- =================================
                         IMAGES
                    ================================== -->

                    <section
                        class="admin-editor-section"
                    >

                        <h3
                            class="admin-editor-section-title"
                        >
                            Book Images
                        </h3>


                        <div
                            class="admin-form-grid"
                        >

                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="bookCoverImage"
                                >
                                    Cover Image URL
                                </label>

                                <input
                                    type="text"
                                    id="bookCoverImage"
                                    class="admin-input"
                                    placeholder="/static/uploads/books/cover.jpg"
                                >

                            </div>


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="bookBannerImage"
                                >
                                    Banner Image URL
                                </label>

                                <input
                                    type="text"
                                    id="bookBannerImage"
                                    class="admin-input"
                                    placeholder="/static/uploads/books/banner.jpg"
                                >

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="bookFeaturedImage"
                                >
                                    Featured Image URL
                                </label>

                                <input
                                    type="text"
                                    id="bookFeaturedImage"
                                    class="admin-input"
                                    placeholder="/static/uploads/books/featured.jpg"
                                >

                            </div>

                        </div>

                    </section>


                    <!-- =================================
                         PUBLISH SETTINGS
                    ================================== -->

                    <section
                        class="admin-editor-section"
                    >

                        <h3
                            class="admin-editor-section-title"
                        >
                            Publishing
                        </h3>


                        <div
                            class="admin-form-grid"
                        >

                            <label
                                class="admin-checkbox-row"
                            >

                                <input
                                    type="checkbox"
                                    id="bookPublished"
                                    class="admin-checkbox"
                                >

                                <span
                                    class="admin-checkbox-label"
                                >
                                    Published
                                </span>

                            </label>


                            <label
                                class="admin-checkbox-row"
                            >

                                <input
                                    type="checkbox"
                                    id="bookFeatured"
                                    class="admin-checkbox"
                                >

                                <span
                                    class="admin-checkbox-label"
                                >
                                    Featured Book
                                </span>

                            </label>

                        </div>

                    </section>


                    <!-- =================================
                         SEO
                    ================================== -->

                    <section
                        class="admin-editor-section"
                    >

                        <h3
                            class="admin-editor-section-title"
                        >
                            SEO Settings
                        </h3>


                        <div
                            class="admin-form-grid"
                        >

                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="seoMetaTitle"
                                >
                                    Meta Title
                                </label>

                                <input
                                    type="text"
                                    id="seoMetaTitle"
                                    class="admin-input"
                                    placeholder="SEO title"
                                >

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="seoMetaDescription"
                                >
                                    Meta Description
                                </label>

                                <textarea
                                    id="seoMetaDescription"
                                    class="admin-textarea"
                                    placeholder="SEO description"
                                ></textarea>

                            </div>


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="seoFocusKeyword"
                                >
                                    Focus Keyword
                                </label>

                                <input
                                    type="text"
                                    id="seoFocusKeyword"
                                    class="admin-input"
                                    placeholder="Primary keyword"
                                >

                            </div>


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="seoRobots"
                                >
                                    Robots
                                </label>

                                <input
                                    type="text"
                                    id="seoRobots"
                                    class="admin-input"
                                    value="index, follow"
                                >

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="seoCanonicalUrl"
                                >
                                    Canonical URL
                                </label>

                                <input
                                    type="text"
                                    id="seoCanonicalUrl"
                                    class="admin-input"
                                    placeholder="/books/book-slug"
                                >

                            </div>


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="seoOgTitle"
                                >
                                    OG Title
                                </label>

                                <input
                                    type="text"
                                    id="seoOgTitle"
                                    class="admin-input"
                                >

                            </div>


                            <div
                                class="admin-form-group"
                            >

                                <label
                                    class="admin-label"
                                    for="seoOgImage"
                                >
                                    OG Image
                                </label>

                                <input
                                    type="text"
                                    id="seoOgImage"
                                    class="admin-input"
                                >

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="seoOgDescription"
                                >
                                    OG Description
                                </label>

                                <textarea
                                    id="seoOgDescription"
                                    class="admin-textarea"
                                ></textarea>

                            </div>


                            <div
                                class="admin-form-group full"
                            >

                                <label
                                    class="admin-label"
                                    for="seoSchemaData"
                                >
                                    JSON-LD Schema
                                </label>

                                <textarea
                                    id="seoSchemaData"
                                    class="admin-textarea"
                                    style="min-height:180px;"
                                    placeholder='{"@context":"https://schema.org"}'
                                ></textarea>

                            </div>

                        </div>

                    </section>

                </form>

            </div>


            <div class="admin-modal-footer">

                <button
                    type="button"
                    id="cancelBookBtn"
                    class="admin-btn admin-btn-secondary"
                >
                    Cancel
                </button>


                <button
                    type="submit"
                    form="bookForm"
                    id="saveBookBtn"
                    class="admin-btn admin-btn-primary"
                >
                    Create Book
                </button>

            </div>

        </div>
        `;


    document.body.appendChild(
        modal
    );
}


/* =========================================================
   33. OPEN MODAL
========================================================= */

function openAdminBookModalElement() {

    const modal =
        adminBookElement(
            "bookModal"
        );


    if (!modal) {

        return;
    }


    modal.classList.add(
        "active"
    );


    document.body.style.overflow =
        "hidden";
}


/* =========================================================
   34. CLOSE MODAL
========================================================= */

function closeAdminBookModal() {

    const modal =
        adminBookElement(
            "bookModal"
        );


    if (!modal) {

        return;
    }


    modal.classList.remove(
        "active"
    );


    document.body.style.overflow =
        "";


    const form =
        adminBookElement(
            "bookForm"
        );


    if (form) {

        form.reset();
    }


    AdminBooksState.editingBookId =
        null;
}


/* =========================================================
   35. CONFIRM MODAL
========================================================= */

let adminBookConfirmResolver =
    null;


function showAdminBookConfirm(
    title,
    message
) {

    return new Promise(
        resolve => {

            adminBookConfirmResolver =
                resolve;


            let overlay =
                adminBookElement(
                    "adminBookConfirmModal"
                );


            if (!overlay) {

                overlay =
                    document.createElement(
                        "div"
                    );

                overlay.id =
                    "adminBookConfirmModal";

                overlay.className =
                    "admin-modal-overlay";


                overlay.innerHTML =
                    `
                    <div
                        class="admin-modal admin-modal-sm"
                    >

                        <div class="admin-modal-header">

                            <h2
                                id="adminBookConfirmTitle"
                                class="admin-modal-title"
                            >
                            </h2>

                            <button
                                type="button"
                                class="admin-modal-close"
                                id="adminBookConfirmClose"
                            >
                                ×
                            </button>

                        </div>


                        <div class="admin-modal-body">

                            <div
                                class="admin-confirm"
                            >

                                <div
                                    class="admin-confirm-icon"
                                >
                                    ⚠️
                                </div>


                                <h3
                                    id="adminBookConfirmMessage"
                                    class="admin-confirm-title"
                                >
                                </h3>

                            </div>

                        </div>


                        <div class="admin-modal-footer">

                            <button
                                type="button"
                                id="adminBookConfirmCancel"
                                class="admin-btn admin-btn-secondary"
                            >
                                Cancel
                            </button>


                            <button
                                type="button"
                                id="adminBookConfirmYes"
                                class="admin-btn admin-btn-danger"
                            >
                                Delete
                            </button>

                        </div>

                    </div>
                    `;


                document.body.appendChild(
                    overlay
                );


                overlay
                    .querySelector(
                        "#adminBookConfirmClose"
                    )
                    .addEventListener(
                        "click",
                        () => {

                            resolveAdminBookConfirm(
                                false
                            );

                        }
                    );


                overlay
                    .querySelector(
                        "#adminBookConfirmCancel"
                    )
                    .addEventListener(
                        "click",
                        () => {

                            resolveAdminBookConfirm(
                                false
                            );

                        }
                    );


                overlay
                    .querySelector(
                        "#adminBookConfirmYes"
                    )
                    .addEventListener(
                        "click",
                        () => {

                            resolveAdminBookConfirm(
                                true
                            );

                        }
                    );
            }


            const titleElement =
                adminBookElement(
                    "adminBookConfirmTitle"
                );

            const messageElement =
                adminBookElement(
                    "adminBookConfirmMessage"
                );


            if (titleElement) {

                titleElement.textContent =
                    title;
            }


            if (messageElement) {

                messageElement.textContent =
                    message;
            }


            overlay.classList.add(
                "active"
            );

            document.body.style.overflow =
                "hidden";
        }
    );
}


/* =========================================================
   36. RESOLVE CONFIRM
========================================================= */

function resolveAdminBookConfirm(
    value
) {

    const resolver =
        adminBookConfirmResolver;


    adminBookConfirmResolver =
        null;


    closeAdminBookConfirm();


    if (resolver) {

        resolver(
            value
        );
    }
}


/* =========================================================
   37. CLOSE CONFIRM
========================================================= */

function closeAdminBookConfirm() {

    const overlay =
        adminBookElement(
            "adminBookConfirmModal"
        );


    if (!overlay) {

        return;
    }


    overlay.classList.remove(
        "active"
    );


    document.body.style.overflow =
        "";
}


/* =========================================================
   38. GLOBAL FUNCTIONS
========================================================= */

window.loadAdminBooks =
    loadAdminBooks;

window.openAdminBookModal =
    openAdminBookModal;

window.closeAdminBookModal =
    closeAdminBookModal;

window.editAdminBook =
    editAdminBook;

window.deleteAdminBook =
    deleteAdminBook;

window.toggleAdminBookPublished =
    toggleAdminBookPublished;

window.toggleAdminBookFeatured =
    toggleAdminBookFeatured;


/* =========================================================
   END OF ADMIN BOOKS JAVASCRIPT
========================================================= */
