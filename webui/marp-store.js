import { createStore } from "/js/AlpineStore.js";
import { callJsonApi } from "/js/api.js";
import { toastFrontendError, toastFrontendSuccess, toastFrontendInfo } from "/components/notifications/notification-store.js";

export const store = createStore("marpStore", {
    // State
    _initialized: false,
    panelOpen: false,
    files: [],
    currentFile: "",
    currentContent: "",
    renderedHtml: "",
    renderedCss: "",
    slideCount: 0,
    currentSlide: 0,
    slideHtmls: [],  // individual slide HTML strings
    exportLoading: false,
    exportDropdownOpen: false,
    filesLoading: false,
    rendering: false,

    // Lifecycle
    init() {
        if (this._initialized) return;
        this._initialized = true;
    },

    // Panel toggle
    togglePanel() {
        this.panelOpen = !this.panelOpen;
        if (this.panelOpen && this.files.length === 0) {
            this.loadFileList();
        }
    },

    openPanel() {
        this.panelOpen = true;
        if (this.files.length === 0) this.loadFileList();
    },

    closePanel() {
        this.panelOpen = false;
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

    backToList() {
        this.currentFile = "";
        this.currentContent = "";
        this.renderedHtml = "";
        this.renderedCss = "";
        this.slideHtmls = [];
        this.slideCount = 0;
        this.currentSlide = 0;
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
            // Parse individual slides from rendered HTML
            this._parseSlides(res.html, res.css);
            // Inject current slide
            this._injectCurrentSlide();
        } catch (e) {
            toastFrontendError("Could not render slides: " + e.message);
        } finally {
            this.rendering = false;
        }
    },

    _parseSlides(html, css) {
        // Count slides from SVG tags in HTML
        const matches = html.match(/data-marpit-svg/g);
        this.slideCount = matches ? matches.length : 0;
        this.slideHtmls = []; // not used in iframe mode
    },

    _injectCurrentSlide() {
        const container = document.getElementById("marp-slide-display");
        if (!container) {
            setTimeout(() => this._injectCurrentSlide(), 100);
            return;
        }
        if (this.slideCount === 0) {
            container.innerHTML = '<p style="opacity:0.4;text-align:center;padding:20px">No slides</p>';
            return;
        }
        const idx = Math.max(0, Math.min(this.currentSlide, this.slideCount - 1));

        // Reuse or create the iframe
        let iframe = container.querySelector('iframe#marp-iframe');
        if (!iframe) {
            container.innerHTML = '';
            iframe = document.createElement('iframe');
            iframe.id = 'marp-iframe';
            iframe.style.cssText = 'border:none;width:100%;height:100%;background:#0f0f1a;border-radius:4px;';
            container.appendChild(iframe);

            // Write full Marp output into the iframe
            const slideCSS = `
                * { margin:0; padding:0; box-sizing:border-box; }
                body { overflow:hidden; background:#0f0f1a; display:flex; align-items:center; justify-content:center; width:100vw; height:100vh; }
                svg[data-marpit-svg] { display:none; width:100vw; height:100vh; max-width:100%; max-height:100%; }
                svg[data-marpit-svg].marp-active { display:block; }
            `;
            const iDoc = iframe.contentDocument || iframe.contentWindow.document;
            iDoc.open();
            iDoc.write(`<!DOCTYPE html><html><head><style>${slideCSS}${this.renderedCss}</style></head><body>${this.renderedHtml}</body></html>`);
            iDoc.close();
        }

        // Show only the current slide
        try {
            const iDoc = iframe.contentDocument || iframe.contentWindow.document;
            const svgs = iDoc.querySelectorAll('svg[data-marpit-svg]');
            svgs.forEach((svg, i) => {
                svg.classList.toggle('marp-active', i === idx);
            });
        } catch(e) {
            console.warn('Marp iframe access error:', e);
        }
    },

    // Slide navigation
    prevSlide() {
        if (this.currentSlide > 0) {
            this.currentSlide--;
            this._injectCurrentSlide();
        }
    },

    nextSlide() {
        if (this.currentSlide < this.slideCount - 1) {
            this.currentSlide++;
            this._injectCurrentSlide();
        }
    },

    goToSlide(index) {
        if (index >= 0 && index < this.slideCount) {
            this.currentSlide = index;
            this._injectCurrentSlide();
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
