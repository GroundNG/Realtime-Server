import os
import glob
import re

directory = "/home/umang/ObsidianProjects/prep/prep/Private & Shared"
html_files = glob.glob(os.path.join(directory, "*.html"))

new_script = """
<script>
document.addEventListener("DOMContentLoaded", () => {
    const pageBody = document.querySelector(".page-body");
    if(pageBody) {
        pageBody.setAttribute("contenteditable", "true");
        
        document.querySelectorAll("a").forEach(el => {
            el.addEventListener("click", (e) => {
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                }
            });
        });
    }

    function focusElement(el) {
        el.focus();
        const sel = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(true);
        sel.removeAllRanges();
        sel.addRange(range);
    }

    // Add Hover Button
    const hoverBtn = document.createElement("div");
    hoverBtn.id = "notion-hover-btn";
    hoverBtn.innerHTML = "+";
    hoverBtn.style.position = "absolute";
    hoverBtn.style.width = "20px";
    hoverBtn.style.height = "20px";
    hoverBtn.style.borderRadius = "3px";
    hoverBtn.style.display = "none";
    hoverBtn.style.alignItems = "center";
    hoverBtn.style.justifyContent = "center";
    hoverBtn.style.cursor = "pointer";
    hoverBtn.style.color = "#aaa";
    hoverBtn.style.fontSize = "16px";
    hoverBtn.style.fontWeight = "bold";
    hoverBtn.style.userSelect = "none";
    hoverBtn.style.zIndex = "1000";
    hoverBtn.style.backgroundColor = "transparent";
    
    hoverBtn.onmouseover = () => { hoverBtn.style.backgroundColor = "#eee"; hoverBtn.style.color = "#333"; };
    hoverBtn.onmouseout = () => { hoverBtn.style.backgroundColor = "transparent"; hoverBtn.style.color = "#aaa"; };
    
    document.body.appendChild(hoverBtn);

    let currentBlock = null;

    document.addEventListener("mousemove", (e) => {
        if (!pageBody) return;
        if (e.target === hoverBtn || hoverBtn.contains(e.target)) return;
        
        const block = e.target.closest("p, h1, h2, h3, h4, h5, h6, ul, ol, div.code-wrap, details, summary");
        if (block && pageBody.contains(block)) {
            currentBlock = block;
            const rect = block.getBoundingClientRect();
            hoverBtn.style.display = "flex";
            hoverBtn.style.top = (window.scrollY + rect.top + (rect.height / 2) - 10) + "px";
            hoverBtn.style.left = (window.scrollX + Math.max(0, rect.left - 25)) + "px";
        } else if (!pageBody.contains(e.target)) {
            if (currentBlock) {
                const rect = currentBlock.getBoundingClientRect();
                if (e.clientX < rect.left - 40 || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) {
                    hoverBtn.style.display = "none";
                    currentBlock = null;
                }
            }
        }
    });

    hoverBtn.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentBlock) {
            const newToggle = document.createElement("ul");
            newToggle.className = "toggle";
            newToggle.innerHTML = '<li><details open><summary>New Toggle</summary><div style="display:contents" dir="auto"><p><br></p></div></details></li>';
            currentBlock.insertAdjacentElement('afterend', newToggle);
            const newSum = newToggle.querySelector("summary");
            if (newSum) focusElement(newSum);
        }
    });

    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
            e.preventDefault();
            hoverBtn.remove();
            
            const currentHTML = document.documentElement.outerHTML;
            fetch("/save", {
                method: "POST",
                body: currentHTML
            }).then(r => {
                if(r.ok) {
                    const toast = document.createElement("div");
                    toast.textContent = "Saved!";
                    toast.style.position = "fixed";
                    toast.style.bottom = "20px";
                    toast.style.right = "20px";
                    toast.style.background = "#4CAF50";
                    toast.style.color = "white";
                    toast.style.padding = "10px 20px";
                    toast.style.borderRadius = "5px";
                    toast.style.zIndex = "10000";
                    document.body.appendChild(toast);
                    setTimeout(() => toast.remove(), 2000);
                }
            }).catch(err => {
                console.error("Save failed", err);
                alert("Failed to save!");
            }).finally(() => {
                document.body.appendChild(hoverBtn);
            });
            return;
        }

        if (e.key === ' ' || e.key === 'Enter') {
            const selection = window.getSelection();
            if (!selection.rangeCount) return;
            const range = selection.getRangeAt(0);
            const node = range.startContainer;
            const element = node.nodeType === 3 ? node.parentElement : node;

            let isSlashCommand = false;
            
            if (node.nodeType === 3) { 
                const textBeforeCursor = node.textContent.substring(0, range.startOffset);
                const isToggle = textBeforeCursor.endsWith("/toggle") && (textBeforeCursor.length === 7 || textBeforeCursor[textBeforeCursor.length - 8].trim() === '');
                const isCode = textBeforeCursor.endsWith("/code") && (textBeforeCursor.length === 5 || textBeforeCursor[textBeforeCursor.length - 6].trim() === '');
                
                if (isToggle || isCode) {
                    e.preventDefault();
                    isSlashCommand = true;
                    
                    const lengthToDelete = isToggle ? 7 : 5;
                    range.setStart(node, range.startOffset - lengthToDelete);
                    range.deleteContents();
                    
                    if (isToggle) {
                        const newToggle = document.createElement("ul");
                        newToggle.className = "toggle";
                        newToggle.innerHTML = '<li><details open><summary>New Toggle</summary><div style="display:contents" dir="auto"><p><br></p></div></details></li>';
                        const targetBlock = element.closest('p, div[style*="display:contents"], pre, summary, li, ul.toggle') || element;
                        if (targetBlock && targetBlock.parentElement) {
                            targetBlock.parentElement.insertBefore(newToggle, targetBlock.nextSibling);
                        } else {
                            element.insertAdjacentElement('afterend', newToggle);
                        }
                        const newSum = newToggle.querySelector("summary");
                        if (newSum) focusElement(newSum);
                    } else if (isCode) {
                        const newCode = document.createElement("div");
                        newCode.setAttribute("style", "display:contents");
                        newCode.setAttribute("dir", "auto");
                        newCode.innerHTML = '<pre class="code code-wrap" style="background: black; color: white; padding: 1em; border-radius: 5px; min-height: 2em;"><code style="background: black; color: white;"><br></code></pre>';
                        const targetBlock = element.closest('p, div[style*="display:contents"], pre, summary') || element;
                        if (targetBlock && targetBlock.parentElement) {
                            targetBlock.parentElement.insertBefore(newCode, targetBlock.nextSibling);
                        } else {
                            element.insertAdjacentElement('afterend', newCode);
                        }
                        const codeEl = newCode.querySelector("code");
                        if (codeEl) focusElement(codeEl);
                    }
                    return;
                }
            }

            if (!isSlashCommand && e.key === 'Enter') {
                const summary = element.closest ? element.closest('summary') : null;
                const details = element.closest ? element.closest('details') : null;

                if (summary) {
                    // Enter inside <summary> -> Add a NEW TOGGLE LIST BLOCK
                    e.preventDefault();
                    const currentToggleItem = summary.closest('li') || summary.closest('ul.toggle') || details;
                    const newToggle = document.createElement("ul");
                    newToggle.className = "toggle";
                    newToggle.innerHTML = '<li><details open><summary>New Toggle</summary><div style="display:contents" dir="auto"><p><br></p></div></details></li>';

                    if (currentToggleItem && currentToggleItem.parentElement) {
                        currentToggleItem.parentElement.insertBefore(newToggle, currentToggleItem.nextSibling);
                    } else {
                        summary.insertAdjacentElement('afterend', newToggle);
                    }
                    const newSum = newToggle.querySelector("summary");
                    if (newSum) focusElement(newSum);
                } else if (details) {
                    // Enter inside <details> body -> Add a NEW LINE inside the toggle block
                    e.preventDefault();
                    const currentLineBlock = element.closest('div[style*="display:contents"], p, pre') || element;
                    const newLineDiv = document.createElement("div");
                    newLineDiv.setAttribute("style", "display:contents");
                    newLineDiv.setAttribute("dir", "auto");
                    newLineDiv.innerHTML = '<p><br></p>';

                    if (currentLineBlock && currentLineBlock.parentElement && details.contains(currentLineBlock.parentElement)) {
                        currentLineBlock.parentElement.insertBefore(newLineDiv, currentLineBlock.nextSibling);
                    } else {
                        details.appendChild(newLineDiv);
                    }
                    const newP = newLineDiv.querySelector("p");
                    if (newP) focusElement(newP);
                }
            }
        }
    });
});
</script>
"""

def inject_code_block(match):
    summary = match.group(0)
    return summary + '\n<div style="display:contents" dir="auto"><pre class="code code-wrap" style="background: black; color: white; padding: 1em; border-radius: 5px; min-height: 2em;"><code style="background: black; color: white;"></code></pre></div>'

for file_path in html_files:
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Remove old injected script entirely if present
    html = re.sub(r'<script>\s*document\.addEventListener\("DOMContentLoaded".*?</script>', '', html, flags=re.DOTALL)

    # Remove any previously injected black background code blocks first
    html = re.sub(r'\n<div style="display:contents" dir="auto"><pre class="code code-wrap" style="background: black; color: white;[^>]+><code style="background: black; color: white;">.*?</code></pre></div>', '', html, flags=re.DOTALL)
    
    # Now inject the automatic code blocks
    html = re.sub(r'(<summary>.*?</summary>)', inject_code_block, html, flags=re.DOTALL)

    # Finally append the script so its string literals are not modified by the above re.sub
    html = html.replace("</body>", new_script + "\n</body>")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"HTML successfully updated for: {os.path.basename(file_path)}")
