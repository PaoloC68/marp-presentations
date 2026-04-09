#!/usr/bin/env node
/**
 * Server-side Marp renderer.
 * Usage: echo '{"markdown":"# Hi"}' | node render.js
 * Output: JSON {"html":"...","css":"...","slideCount":N}
 */
const { Marp } = require(require('path').join(__dirname, '../node_modules/@marp-team/marp-core'));

let input = '';
process.stdin.setEncoding('utf-8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
    try {
        const data = JSON.parse(input);
        const marp = new Marp({ script: false, html: false });
        const { html, css, comments } = marp.render(data.markdown || '');
        // Count slides by counting <svg data-marpit-svg> tags
        const slideCount = (html.match(/data-marpit-svg/g) || []).length;
        const result = JSON.stringify({ html, css, slideCount, comments });
        process.stdout.write(result);
    } catch (e) {
        process.stdout.write(JSON.stringify({ error: e.message }));
        process.exit(1);
    }
});
