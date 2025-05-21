/**
 * Formatting scripts to make the markdown work in html
 */

function applyCustomHighlights(md) {
    return md.replace(/\*\*(.+?)\*\*/g, '<span class="highlight">$1</span>');
}

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

    // Replace **text** with span everywhere in the md-file
    md = applyCustomHighlights(md);

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
                const rawContent = calloutLines.join('\n');
                const highlightedContent = applyCustomHighlights(rawContent);
                const content = marked.parseInline(highlightedContent);
                result.push(`<div class="callout ${calloutType}"><span class="icon">${icon}</span> ${content}</div>`);
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
        const rawContent = calloutLines.join('\n');
        const highlightedContent = applyCustomHighlights(rawContent);
        const content = marked.parseInline(highlightedContent);
        result.push(`<div class="callout ${calloutType}"><span class="icon">${icon}</span><strong>${calloutType.charAt(0).toUpperCase() + calloutType.slice(1)}:</strong> ${content}</div>`);
    }

    return result.join('\n');
}

const sourceTextarea = document.getElementById('source');
const originalMarkdown = sourceTextarea.value;
const processedMarkdown = preprocessMarkdown(originalMarkdown);

const slideshow = remark.create({ source: processedMarkdown });

mermaid.initialize({ startOnLoad: true });

// Render mermaid on slide change
Reveal.on('slidechanged', () => {
    mermaid.run({
        querySelector: '.mermaid'
    });

    // 🟡 Inject breadcrumb as <blockquote> to match existing styling
    const currentSlide = Reveal.getCurrentSlide();
    const breadcrumb = currentSlide.getAttribute('data-breadcrumb');
    const subbreadcrumb = currentSlide.getAttribute('data-subbreadcrumb');

    // Remove old breadcrumb blockquote if it exists
    const oldBreadcrumb = currentSlide.querySelector('blockquote[data-generated-breadcrumb]');
    if (oldBreadcrumb) oldBreadcrumb.remove();

    if (breadcrumb) {
        const bq = document.createElement('blockquote');
        bq.setAttribute('data-generated-breadcrumb', 'true');

        const parsedMain = marked.parseInline(applyCustomHighlights(breadcrumb));
        const parsedSub = subbreadcrumb ? marked.parseInline(applyCustomHighlights(subbreadcrumb)) : '';
        bq.innerHTML = `${parsedMain}${parsedSub ? `<br>${parsedSub}` : ''}`;

        currentSlide.prepend(bq);
    }
});

// Render on initial load too
document.addEventListener('DOMContentLoaded', () => {
    mermaid.run({
        querySelector: '.mermaid'
    });
});
