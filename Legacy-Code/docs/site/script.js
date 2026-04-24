
// Theme Logic
const themeToggleButton = document.getElementById('theme-toggle');
const root = document.documentElement;
const storedTheme = localStorage.getItem('theme');

const setTheme = (theme) => {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
};

// Initial Theme Check
if (storedTheme) {
    setTheme(storedTheme);
} else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(prefersDark ? 'dark' : 'light');
}

if (themeToggleButton) {
    themeToggleButton.addEventListener('click', () => {
        const currentTheme = root.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
}

// Mobile Sidebar Logic
const menuButton = document.getElementById('menu-button');
const sidebar = document.querySelector('.sidebar');
const overlay = document.querySelector('.overlay');

if (menuButton) {
    menuButton.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    });
}

if (overlay) {
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    });
}

// --- Features ---

// 1. Copy to Clipboard
function addCopyButtons() {
    document.querySelectorAll('pre').forEach(pre => {
        // Create button
        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.textContent = 'Copy';
        btn.ariaLabel = 'Copy source code';

        // Add click event
        btn.addEventListener('click', () => {
            const code = pre.querySelector('code');
            const text = code ? code.innerText : pre.innerText;

            navigator.clipboard.writeText(text).then(() => {
                btn.textContent = 'Copied!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = 'Copy';
                    btn.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy mode', err);
                btn.textContent = 'Error';
            });
        });

        pre.appendChild(btn);
    });
}

// 2. Advanced Syntax Highlighting
// We use a multi-pass token replacement strategy to safely highlight keywords without breaking strings.
const PYTHON_KEYWORDS = [
    'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or',
    'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'True', 'False', 'None'
];

const BUILTINS = [
    'print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'super', 'isinstance', 'type'
];

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function highlightPython(code) {
    // 1. Tokenize Strings and Comments to protect them
    const tokens = [];
    const save = (type, content) => {
        const id = `__TOKEN_${tokens.length}__`;
        tokens.push({ id, type, content });
        return id;
    };

    // Regex for docstrings, strings, comments
    // Note: JS Regex doesn't support recursive matching, so we do best effort for simple cases

    let processed = code;

    // Save Docstrings/Multi-line strings (triple quotes)
    processed = processed.replace(/("""[\s\S]*?"""|'''[\s\S]*?''')/g, match => save('s', match));

    // Save Strings (single/double quotes)
    processed = processed.replace(/(".*?"|'.*?')/g, match => save('s', match));

    // Save Comments
    processed = processed.replace(/(#.*)/g, match => save('c', match));

    // 2. Highlight Code

    // Keywords
    PYTHON_KEYWORDS.forEach(kw => {
        const regex = new RegExp(`\\b(${kw})\\b`, 'g');
        processed = processed.replace(regex, '<span class="k">$1</span>');
    });

    // Builtins
    BUILTINS.forEach(kw => {
        const regex = new RegExp(`\\b(${kw})\\b`, 'g');
        processed = processed.replace(regex, '<span class="v">$1</span>'); // Using 'v' (value) color for builtins
    });

    // Numbers
    processed = processed.replace(/\b(\d+)\b/g, '<span class="n">$1</span>');

    // Decorators
    processed = processed.replace(/(@[\w\.]+)/g, '<span class="d">$1</span>');

    // Functions/Classes (def foo, class Bar)
    processed = processed.replace(/\b(def|class)\s+(\w+)/g, '<span class="k">$1</span> <span class="f">$2</span>');

    // 3. Restore Tokens
    tokens.forEach(token => {
        const span = `<span class="${token.type}">${escapeHtml(token.content)}</span>`;
        processed = processed.replace(token.id, span);
    });

    return processed;
}

function runHighlighter() {
    document.querySelectorAll('pre code').forEach(block => {
        // Skip if already highlighted
        if (block.querySelector('span')) return;

        // Detect Language
        const classes = block.className.split(' ');
        const isPython = classes.includes('language-python');

        if (isPython) {
            // Get raw text
            const raw = block.innerText;
            // Highlight
            const highlighted = highlightPython(raw);
            // Apply
            block.innerHTML = highlighted;
        }
        // Can add HTML/XML lexer here if needed
    });
}

document.addEventListener('DOMContentLoaded', () => {
    runHighlighter();
    addCopyButtons();
});
