import os
import re

file_path = "/home/umang/ObsidianProjects/prep/prep/Private & Shared/Cisco ca11832d3bf645cfbd2bb1da3b25dc0c.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Collapse all details
html = html.replace('<details open="">', '<details>')
html = html.replace('<details open>', '<details>')

# Inject script before </body>
script = """
<script>
document.addEventListener("DOMContentLoaded", () => {
    const pageBody = document.querySelector(".page-body");
    if(pageBody) {
        pageBody.setAttribute("contenteditable", "true");
        
        // Prevent default navigation for links inside contenteditable
        document.querySelectorAll("a").forEach(el => {
            el.addEventListener("click", (e) => {
                if (e.ctrlKey || e.metaKey) {
                    // Let it navigate if they hold Ctrl/Cmd
                } else {
                    e.preventDefault();
                }
            });
        });
    }

    let lastSavedHTML = pageBody ? pageBody.innerHTML : "";

    setInterval(() => {
        const currentHTML = document.documentElement.outerHTML;
        // Optimization: only save if content actually changed
        // We will just save the whole document.
        fetch("/save", {
            method: "POST",
            body: currentHTML
        }).then(r => {
            if(r.ok) console.log("Saved at " + new Date().toLocaleTimeString());
        }).catch(e => console.error("Save failed", e));
    }, 5000); // 5 seconds interval for quick saving
});
</script>
"""

if "<script>document.addEventListener" not in html:
    html = html.replace("</body>", script + "</body>")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("HTML modified successfully")
