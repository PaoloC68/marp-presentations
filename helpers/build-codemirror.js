// esbuild entry point — bundles CodeMirror 6 for browser use
// Run: node_modules/.bin/esbuild helpers/build-codemirror.js --bundle --format=esm --outfile=webui/codemirror-bundle.js --minify
export { EditorView, basicSetup } from 'codemirror';
export { EditorState } from '@codemirror/state';
export { markdown } from '@codemirror/lang-markdown';
export { oneDark } from '@codemirror/theme-one-dark';
