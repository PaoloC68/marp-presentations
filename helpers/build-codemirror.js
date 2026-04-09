// esbuild entry point — bundles CodeMirror 6 for browser use
// All @codemirror/state packages are pinned to 6.6.0 via package.json to avoid duplicate instances.
// Build: node_modules/.bin/esbuild helpers/build-codemirror.js --bundle --format=iife --global-name=CodeMirrorBundle --outfile=webui/codemirror-bundle.js --minify
export { EditorView, basicSetup } from 'codemirror';
export { EditorState } from '@codemirror/state';
export { markdown } from '@codemirror/lang-markdown';
export { oneDark } from '@codemirror/theme-one-dark';
