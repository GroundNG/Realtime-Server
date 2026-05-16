import os
import re

file_path = "/home/umang/ObsidianProjects/prep/prep/Private & Shared/Cisco ca11832d3bf645cfbd2bb1da3b25dc0c.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update the injected JavaScript
# We will replace the old script with the new one
old_script_start = '<script>\ndocument.addEventListener("DOMContentLoaded", () => {'
if old_script_start in html:
    # Remove the old script
    html = re.sub(r'<script>\ndocument\.addEventListener\("DOMContentLoaded".*?</script>', '', html, flags=re.DOTALL)

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

    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
            e.preventDefault();
            const currentHTML = document.documentElement.outerHTML;
            fetch("/save", {
                method: "POST",
                body: currentHTML
            }).then(r => {
                if(r.ok) {
                    // Create a tiny toast notification
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
            }).catch(e => {
                console.error("Save failed", e);
                alert("Failed to save!");
            });
        }
    });
});
</script>
"""
html = html.replace("</body>", new_script + "</body>")


# 2. Add code block section at the top of each toggle list with a black background
# Notion toggles are <details><summary>Title</summary>...
# We will insert a pre/code block immediately after <summary>...</summary>
def inject_code_block(match):
    summary = match.group(0)
    return summary + '\n<div style="display:contents" dir="auto"><pre class="code code-wrap" style="background: black; color: white; padding: 1em; border-radius: 5px; min-height: 2em;"><code style="background: black; color: white;"></code></pre></div>'

# We split the html by <details> to carefully inject after the FIRST <summary> in each details, 
# but simply substituting <summary> is easier, as long as we don't double inject.
# Let's remove any previously injected black background code blocks first (in case we run this multiple times)
html = re.sub(r'\n<div style="display:contents" dir="auto"><pre class="code code-wrap" style="background: black; color: white;[^>]+><code style="background: black; color: white;">.*?</code></pre></div>', '', html, flags=re.DOTALL)

# Now inject it
html = re.sub(r'(<summary>.*?</summary>)', inject_code_block, html, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)

print("HTML successfully updated with Ctrl+S save and code blocks.")
