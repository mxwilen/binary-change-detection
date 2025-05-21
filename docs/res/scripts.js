function preprocessMarkdown(md) {
    const iconMap = {
        note: '📝',
        tip: '💡',
        important: '⚠️',
        warning: '🚨',
        info: 'ℹ️',
        question: '❓',
        check: '✅'
    };

    const lines = md.split('\n');
    const result = [];
    let insideCallout = false;
    let calloutType = '';
    let calloutLines = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        const match = line.match(/^\s*>\s*\[!(\w+)\]\s*$/);
        if (match) {
            insideCallout = true;
            calloutType = match[1].toLowerCase();
            calloutLines = [];
            continue;
        }

        if (insideCallout) {
            if (/^\s*>/.test(line)) {
                calloutLines.push(line.replace(/^\s*>?\s?/, ''));
            } else {
                const icon = iconMap[calloutType] || '📌';
                const content = marked.parseInline(calloutLines.join('\n'));
                result.push(`<div class="callout ${calloutType}"><span class="icon">${icon}</span><strong>${calloutType.charAt(0).toUpperCase() + calloutType.slice(1)}:</strong> ${content}</div>`);
                result.push(line);
                insideCallout = false;
            }
        } else {
            result.push(line);
        }
    }

    // Final callout if EOF
    if (insideCallout) {
        const icon = iconMap[calloutType] || '📌';
        const content = marked.parseInline(calloutLines.join('\n'));
        result.push(`<div class="callout ${calloutType}"><span class="icon">${icon}</span><strong>${calloutType.charAt(0).toUpperCase() + calloutType.slice(1)}:</strong> ${content}</div>`);
    }

    return result.join('\n');
}

const sourceTextarea = document.getElementById('source');
const originalMarkdown = sourceTextarea.value;
const processedMarkdown = preprocessMarkdown(originalMarkdown);

mermaid.initialize({ startOnLoad: false });

const slideshow = remark.create({ source: processedMarkdown });

function renderMermaid() {
    const diagrams = document.querySelectorAll('.mermaid');
    diagrams.forEach((el) => {
        if (!el.classList.contains('rendered')) {
            try {
                mermaid.init(undefined, el);
                el.classList.add('rendered');
            } catch (e) {
                console.error('Mermaid render error:', e);
            }
        }
    });
}

// Re-render Mermaid after each slide
slideshow.on('afterShowSlide', () => {
    setTimeout(renderMermaid, 10); // allow slide to be visible
});