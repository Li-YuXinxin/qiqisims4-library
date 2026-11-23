# -*- coding: utf-8 -*-
"""
Sims4 资源站 data.json 可视化编辑器
-------------------------------------------------
字段：title / cover / author / category / gameVer / tags / link / code / desc
运行：python editor.py   （需与 data.json 放在同一目录）
"""

import json
import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

JSON_PATH = "data.json"
CATEGORIES = ["模组推荐", "房屋分享", "家具CC", "服装CC", "实用工具"]

DEFAULT_SITE = {
    "emoji": "📚",
    "title": "柒柒的 Sims4 资源库",
    "notice": "本站仅收录网络公开网盘索引链接，不存储任何资源本体；模组 / CC 版权归原作者所有，"
              "若作者提出删除要求，请联系站长立即下架。",
    "categories": CATEGORIES,
    "pageSize": 12,
}


# ===================== 读写 =====================
def load_data():
    """返回 (site_dict, items_list)。兼容两种格式：{site, items} 或纯数组。"""
    if not os.path.exists(JSON_PATH):
        return dict(DEFAULT_SITE), []
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        messagebox.showerror("JSON 读取错误", f"文件格式有问题：\n{e}")
        return dict(DEFAULT_SITE), []

    if isinstance(raw, list):
        return dict(DEFAULT_SITE), raw
    site = dict(DEFAULT_SITE)
    site.update(raw.get("site") or {})
    return site, raw.get("items") or []


def save_data(site, items):
    """写回 data.json，保留 site 节点；写前自动备份 data.json.bak。"""
    payload = {"site": site, "items": items}
    try:
        if os.path.exists(JSON_PATH):
            shutil.copyfile(JSON_PATH, JSON_PATH + ".bak")
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("保存失败", str(e))
        return False


def split_tags(text):
    """按 英文逗号 / 中文逗号 / 顿号 / 分号 / 换行 拆分标签。"""
    parts = re.split(r"[,，、;；\n]", text or "")
    return [p.strip() for p in parts if p.strip()]


# ===================== 界面 =====================
class EditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sims4 资源库 · data.json 编辑器")
        self.root.geometry("920x700")

        self.site, self.items = load_data()
        self.cur_index = None
        self._loading = False

        self._build_ui()
        self.refresh_table()

    # ---------- UI ----------
    def _build_ui(self):
        # 顶部状态
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=(10, 4))
        ttk.Label(top, text=f"数据文件：{os.path.abspath(JSON_PATH)}",
                  foreground="#666").pack(side=tk.LEFT)
        self.lbl_count = ttk.Label(top, text="", foreground="#2383e2")
        self.lbl_count.pack(side=tk.RIGHT)

        # 表格 + 滚动条
        table_wrap = ttk.Frame(self.root)
        table_wrap.pack(fill=tk.BOTH, expand=False, padx=10)

        cols = ("title", "author", "category", "gameVer", "tags", "code")
        heads = ("标题", "作者", "分类", "版本", "标签", "提取码")
        widths = (250, 110, 100, 80, 180, 70)

        self.tree = ttk.Treeview(table_wrap, columns=cols, show="headings", height=9)
        for c, h, w in zip(cols, heads, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="w")
        vsb = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # 表单
        form = ttk.LabelFrame(self.root, text="编辑条目")
        form.pack(fill=tk.BOTH, padx=10, pady=8)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        self.var_title = tk.StringVar()
        self.var_author = tk.StringVar()
        self.var_cat = tk.StringVar()
        self.var_ver = tk.StringVar()
        self.var_cover = tk.StringVar()
        self.var_tags = tk.StringVar()
        self.var_link = tk.StringVar()
        self.var_code = tk.StringVar()

        r = 0
        ttk.Label(form, text="标题").grid(row=r, column=0, sticky="w", padx=6, pady=3)
        ttk.Entry(form, textvariable=self.var_title).grid(row=r, column=1, columnspan=3, sticky="ew", padx=6)
        r += 1

        ttk.Label(form, text="作者").grid(row=r, column=0, sticky="w", padx=6, pady=3)
        ttk.Entry(form, textvariable=self.var_author).grid(row=r, column=1, sticky="ew", padx=6)
        ttk.Label(form, text="分类").grid(row=r, column=2, sticky="w", padx=6)
        ttk.Combobox(form, textvariable=self.var_cat, values=CATEGORIES,
                     state="readonly").grid(row=r, column=3, sticky="ew", padx=6)
        r += 1

        ttk.Label(form, text="版本").grid(row=r, column=0, sticky="w", padx=6, pady=3)
        ttk.Entry(form, textvariable=self.var_ver).grid(row=r, column=1, sticky="ew", padx=6)
        ttk.Label(form, text="提取码").grid(row=r, column=2, sticky="w", padx=6)
        ttk.Entry(form, textvariable=self.var_code).grid(row=r, column=3, sticky="ew", padx=6)
        r += 1

        ttk.Label(form, text="封面链接").grid(row=r, column=0, sticky="w", padx=6, pady=3)
        ttk.Entry(form, textvariable=self.var_cover).grid(row=r, column=1, columnspan=3, sticky="ew", padx=6)
        r += 1

        ttk.Label(form, text="标签").grid(row=r, column=0, sticky="w", padx=6, pady=3)
        ttk.Entry(form, textvariable=self.var_tags).grid(row=r, column=1, columnspan=3, sticky="ew", padx=6)
        r += 1

        ttk.Label(form, text="网盘链接").grid(row=r, column=0, sticky="w", padx=6, pady=3)
        ttk.Entry(form, textvariable=self.var_link).grid(row=r, column=1, columnspan=3, sticky="ew", padx=6)
        r += 1

        ttk.Label(form, text="详细介绍").grid(row=r, column=0, sticky="nw", padx=6, pady=3)
        self.txt_desc = tk.Text(form, height=7, wrap="word")
        self.txt_desc.grid(row=r, column=1, columnspan=3, sticky="ew", padx=6, pady=(0, 6))
        r += 1

        ttk.Label(form, text="支持 ## 小标题、- 列表、1. 序号；标签支持 , ， 、 分隔",
                  foreground="#888").grid(row=r, column=1, columnspan=3, sticky="w", padx=6, pady=(0, 6))

        # 按钮
        bar = ttk.Frame(self.root)
        bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(bar, text="新增条目", command=self.add_item).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="保存修改", command=self.save_item).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="删除选中", command=self.del_item).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="上移", command=lambda: self.move(-1)).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="下移", command=lambda: self.move(1)).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="清空表单", command=self.clear_form).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="复制本条 JSON", command=self.copy_json).pack(side=tk.RIGHT, padx=3)

        self.txt = None  # 用于提示

    # ---------- 列表 ----------
    def refresh_table(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for i, it in enumerate(self.items):
            self.tree.insert("", "end", iid=str(i), values=(
                it.get("title", ""),
                it.get("author", ""),
                it.get("category", ""),
                it.get("gameVer", ""),
                "、".join(it.get("tags") or []),
                it.get("code", ""),
            ))
        self.lbl_count.config(text=f"共 {len(self.items)} 条")

    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        self.cur_index = idx
        it = self.items[idx]
        self._loading = True
        self.var_title.set(it.get("title", ""))
        self.var_author.set(it.get("author", ""))
        self.var_cat.set(it.get("category", "") or CATEGORIES[0])
        self.var_ver.set(it.get("gameVer", ""))
        self.var_cover.set(it.get("cover", ""))
        self.var_tags.set("、".join(it.get("tags") or []))
        self.var_link.set(it.get("link", ""))
        self.var_code.set(it.get("code", ""))
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", it.get("desc", ""))
        self._loading = False

    def clear_form(self):
        self.cur_index = None
        for v in (self.var_title, self.var_author, self.var_ver,
                  self.var_cover, self.var_tags, self.var_link, self.var_code):
            v.set("")
        self.var_cat.set(CATEGORIES[0])
        self.txt_desc.delete("1.0", tk.END)

    # ---------- 表单 -> dict ----------
    def form_dict(self):
        return {
            "title": self.var_title.get().strip(),
            "cover": self.var_cover.get().strip(),
            "author": self.var_author.get().strip(),
            "category": self.var_cat.get().strip(),
            "gameVer": self.var_ver.get().strip(),
            "tags": split_tags(self.var_tags.get()),
            "link": self.var_link.get().strip(),
            "code": self.var_code.get().strip(),
            "desc": self.txt_desc.get("1.0", tk.END).strip(),
        }

    def _persist(self):
        ok = save_data(self.site, self.items)
        if ok:
            self.refresh_table()
            self.lbl_count.config(text=f"共 {len(self.items)} 条 · 已保存  {self._now()}")
        return ok

    @staticmethod
    def _now():
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    # ---------- 增删改 ----------
    def add_item(self):
        d = self.form_dict()
        if not d["title"]:
            messagebox.showwarning("提示", "标题不能为空")
            return
        if not d["category"]:
            messagebox.showwarning("提示", "请选择分类")
            return
        self.items.append(d)
        if self._persist():
            self.clear_form()
            self.tree.see(str(len(self.items) - 1))
            self.tree.selection_set(str(len(self.items) - 1))

    def save_item(self):
        if self.cur_index is None:
            messagebox.showwarning("提示", "请先在表格里选中一条记录")
            return
        d = self.form_dict()
        if not d["title"]:
            messagebox.showwarning("提示", "标题不能为空")
            return
        if not d["category"]:
            messagebox.showwarning("提示", "请选择分类")
            return
        self.items[self.cur_index] = d
        if self._persist():
            idx = self.cur_index
            self.tree.selection_set(str(idx))
            self.tree.see(str(idx))

    def del_item(self):
        if self.cur_index is None:
            messagebox.showwarning("提示", "请先在表格里选中一条记录")
            return
        title = self.items[self.cur_index].get("title", "")
        if not messagebox.askyesno("确认删除", f"确定删除「{title}」？"):
            return
        del self.items[self.cur_index]
        self.clear_form()
        self._persist()

    def move(self, step):
        if self.cur_index is None:
            return
        new_idx = self.cur_index + step
        if not (0 <= new_idx < len(self.items)):
            return
        self.items[self.cur_index], self.items[new_idx] = \
            self.items[new_idx], self.items[self.cur_index]
        self.cur_index = new_idx
        if self._persist():
            self.tree.selection_set(str(new_idx))
            self.tree.see(str(new_idx))

    def copy_json(self):
        if self.cur_index is None:
            messagebox.showwarning("提示", "请先在表格里选中一条记录")
            return
        text = json.dumps(self.items[self.cur_index], ensure_ascii=False, indent=2)
        win = tk.Toplevel(self.root)
        win.title("本条 JSON")
        win.geometry("560x420")
        box = tk.Text(win, wrap="none")
        box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        box.insert("1.0", text)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        ttk.Label(win, text="已复制到剪贴板", foreground="#2383e2").pack(pady=(0, 8))


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except Exception:
        pass
    EditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
