"""
方格子導流站更新器 — GUI 版
雙擊「更新導流站.bat」就會打開這個視窗
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_FILE = os.path.join(SCRIPT_DIR, "articles.txt")


def load_existing():
    """讀取現有文章數量"""
    count = 0
    if os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and " | " in line:
                    count += 1
    return count


def parse_input(text):
    """
    解析輸入，支援兩種格式：
    格式 1（Word 貼上）：標題在第一行，URL 在第二行，交替排列
    格式 2（手動）：標題 | URL，一行一篇
    """
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    articles = []

    # 判斷格式：如果有 " | " 就是格式 2
    if any(" | " in l for l in lines):
        for l in lines:
            if " | " in l:
                title, url = l.rsplit(" | ", 1)
                if url.startswith("http"):
                    articles.append((title.strip(), url.strip()))
    else:
        # 格式 1：標題和 URL 交替（跟 Word 檔一樣）
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("http"):
                # 如果第一行就是 URL，跳過
                i += 1
                continue
            # 這行是標題，找下面最近的 URL
            title = line
            i += 1
            while i < len(lines) and not lines[i].startswith("http"):
                i += 1
            if i < len(lines) and lines[i].startswith("http"):
                url = lines[i]
                if "vocus.cc" in url:
                    articles.append((title, url))
                i += 1

    return articles


def do_update():
    """新增文章並更新網站"""
    text = input_box.get("1.0", tk.END).strip()

    if not text:
        # 沒有輸入新文章，直接更新現有的
        run_generate_and_push("沒有新增文章，重新生成並更新現有頁面")
        return

    new_articles = parse_input(text)

    if not new_articles:
        messagebox.showwarning("格式錯誤", "沒有找到有效的文章。\n\n支援兩種格式：\n1. 從 Word 直接貼上（標題和網址交替）\n2. 標題 | 網址（一行一篇）")
        return

    # 讀取現有內容，去重
    existing_urls = set()
    if os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if " | " in line and "vocus.cc" in line:
                    _, url = line.rsplit(" | ", 1)
                    existing_urls.add(url.strip())

    # 只加新的
    added = []
    for title, url in new_articles:
        if url not in existing_urls:
            added.append((title, url))

    if not added:
        messagebox.showinfo("沒有新文章", "這些文章都已經在清單裡了")
        return

    # 寫入 articles.txt
    with open(ARTICLES_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n# === 新增 ===\n")
        for title, url in added:
            f.write(f"{title} | {url}\n")

    run_generate_and_push(f"新增了 {len(added)} 篇文章")


def run_generate_and_push(msg):
    """生成頁面並推上 GitHub"""
    status_label.config(text="正在更新...")
    root.update()

    try:
        # 生成 HTML + sitemap
        result = subprocess.run(
            [sys.executable, "-X", "utf8", os.path.join(SCRIPT_DIR, "generate_site.py")],
            capture_output=True, text=True, cwd=SCRIPT_DIR
        )
        if result.returncode != 0:
            messagebox.showerror("生成失敗", result.stderr)
            status_label.config(text="生成失敗")
            return

        # Git push
        git_result = subprocess.run(
            ["git", "add", ".", "&&", "git", "commit", "-m", "Update articles", "&&", "git", "push"],
            capture_output=True, text=True, cwd=SCRIPT_DIR, shell=True
        )

        total = load_existing()
        status_label.config(text=f"{msg}。目前共 {total} 篇。")
        input_box.delete("1.0", tk.END)

        messagebox.showinfo("更新完成",
            f"{msg}\n\n目前共 {total} 篇文章\n\n"
            f"網站會在 1-2 分鐘後更新：\n"
            f"https://liz08210818-code.github.io/vocus-articles/")

    except Exception as e:
        messagebox.showerror("錯誤", str(e))
        status_label.config(text="發生錯誤")


# === GUI ===
root = tk.Tk()
root.title("方格子導流站更新器")
root.geometry("620x520")
root.resizable(False, False)

# 標題
tk.Label(root, text="方格子導流站更新器", font=("Microsoft JhengHei", 14, "bold")).pack(pady=(10, 5))

existing_count = load_existing()
tk.Label(root, text=f"目前已有 {existing_count} 篇文章", font=("Microsoft JhengHei", 10), fg="#666").pack()

# 說明
frame_info = tk.Frame(root)
frame_info.pack(padx=15, pady=(10, 5), fill="x")
tk.Label(frame_info, text="貼上文章標題和方格子網址（從 Word 直接貼上就好）：",
         font=("Microsoft JhengHei", 10), anchor="w").pack(fill="x")
tk.Label(frame_info, text="格式：標題一行、網址一行，交替排列。留空直接按更新 = 只重新生成頁面",
         font=("Microsoft JhengHei", 9), fg="#999", anchor="w").pack(fill="x")

# 輸入框
input_box = scrolledtext.ScrolledText(root, width=70, height=18, font=("Consolas", 10))
input_box.pack(padx=15, pady=5)

# 按鈕
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="更新導流站", command=do_update,
          font=("Microsoft JhengHei", 11, "bold"), bg="#4a90d9", fg="white",
          padx=20, pady=5).pack()

# 狀態列
status_label = tk.Label(root, text="", font=("Microsoft JhengHei", 9), fg="#666")
status_label.pack(pady=(5, 10))

root.mainloop()
