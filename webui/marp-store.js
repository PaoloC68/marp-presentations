import { createStore } from "/js/AlpineStore.js";
import { callJsonApi } from "/js/api.js";
import { toastFrontendError, toastFrontendSuccess, toastFrontendInfo } from "/components/notifications/notification-store.js";

export const store = createStore("marpStore", {
    // State
    _initialized: false,
    files: [],
    currentFile: "",
    currentContent: "",
    renderedHtml: "",
    renderedCss: "",
    slideCount: 0,
    currentSlide: 0,
    exportLoading: false,
    exportDropdownOpen: false,
    filesLoading: false,
    rendering: false,

    // Lifecycle
    init() {
        if (this._initialized) return;
        this._initialized = true;
    },

    async onOpen() {
        await this.loadFileList();
        if (this.currentFile && this.currentContent) {
            await this.renderSlides();
        }
    },

    cleanup() {
        this.exportDropdownOpen = false;
    },

    // File operations
    async loadFileList() {
        this.filesLoading = true;
        try {
            const res = await callJsonApi("/api/plugins/marp-presentations/marp_list", {});
            this.files = res.files || [];
        } catch (e) {
            toastFrontendError("Could not load presentations list: " + e.message);
        } finally {
            this.filesLoading = false;
        }
    },

    async openFile(filename) {
        try {
            const res = await callJsonApi("/api/plugins/marp-presentations/marp_load", { filename });
            this.currentFile = res.filename;
            this.currentContent = res.content;
            this.currentSlide = 0;
            await this.renderSlides();
        } catch (e) {
            toastFrontendError("Could not load file: " + e.message);
        }
    },

    // Server-side rendering
    async renderSlides() {
        if (!this.currentContent) return;
        this.rendering = true;
        try {
            const res = await callJsonApi("/api/plugins/marp-presentations/marp_render", {
                markdown: this.currentContent
            });
            this.renderedHtml = res.html;
            this.renderedCss = res.css;
            this.slideCount = res.slideCount || 0;
            this.currentSlide = 0;
            // Inject into DOM after Alpine updates
            setTimeout(() => this._injectSlides(), 100);
        } catch (e) {
            toastFrontendError("Could not render slides: " + e.message);
        } finally {
            this.rendering = false;
        }
    },

    _injectSlides() {
        const container = document.getElementById("marp-slides-container");
        if (!container) return;
        container.innerHTML = `${this.renderedHtml}<style>${this.renderedCss}</style>`;
    },

    // Slide navigation
    prevSlide() {
        if (this.currentSlide > 0) {
            this.currentSlide--;
            this._scrollToSlide(this.currentSlide);
        }
    },

    nextSlide() {
        if (this.currentSlide < this.slideCount - 1) {
            this.currentSlide++;
            this._scrollToSlide(this.currentSlide);
        }
    },

    goToSlide(index) {
        if (index >= 0 && index < this.slideCount) {
            this.currentSlide = index;
            this._scrollToSlide(index);
        }
    },

    _scrollToSlide(index) {
        const container = document.getElementById("marp-slides-container");
        if (!container) return;
        const svgs = container.querySelectorAll("svg[data-marpit-svg]");
        if (svgs[index]) {
            svgs[index].scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
    },

    // Export
    async exportPresentation(format) {
        if (!this.currentFile) {
            toastFrontendError("No presentation loaded. Open a file first.");
            return;
        }
        this.exportLoading = true;
        this.exportDropdownOpen = false;
        toastFrontendInfo(`Exporting as ${format.toUpperCase()}...`);
        try {
            const res = await callJsonApi("/api/plugins/marp-presentations/marp_export", {
                filename: this.currentFile,
                format
            });
            toastFrontendSuccess(`Exported: ${res.filename}`);
        } catch (e) {
            toastFrontendError("Export failed: " + (e.message || e));
        } finally {
            this.exportLoading = false;
        }
    },
});
