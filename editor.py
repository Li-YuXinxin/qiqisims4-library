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
CATEGORIES = ["房屋分享", "家具CC", "服装CC", "作者推荐", "模组推荐", "实用工具"]
AUTHOR_CATEGORIES = ["房屋作者", "家具作者", "服装作者", "动画作者"]

DEFAULT_SITE = {
    "emoji": "📚",
    "title": "柒柒的 Sims4 资源库",
    "notice": "本站仅收录网络公开网盘索引链接，不存储任何资源本体；模组 / CC 版权归原作者所有，"
              "若作者提出删除要求，请联系站长（🐧1842336774）立即下架。",
    "categories": ["全部", *CATEGORIES],
    "authorCategories": AUTHOR_CATEGORIES,
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

        self.tree = ttk.Treeview(table_wrap, columns=cols, show="headings", height=9,
                                 selectmode="extended")
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
        self.var_author_cat = tk.StringVar()
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
        self.var_cat.trace_add("write", self.update_author_category)
        r += 1

        self.author_cat_label = ttk.Label(form, text="作者分类")
        self.author_cat_label.grid(row=r, column=2, sticky="w", padx=6)
        self.author_cat_combo = ttk.Combobox(form, textvariable=self.var_author_cat,
                                             values=AUTHOR_CATEGORIES, state="readonly")
        self.author_cat_combo.grid(row=r, column=3, sticky="ew", padx=6)
        self.update_author_category()
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

        batch = ttk.LabelFrame(self.root, text="批量操作（表格中可按 Ctrl / Shift 多选）")
        batch.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(batch, text="批量编辑", command=self.batch_edit).pack(side=tk.LEFT, padx=3, pady=5)
        ttk.Button(batch, text="批量删除", command=self.batch_delete).pack(side=tk.LEFT, padx=3, pady=5)
        ttk.Button(batch, text="批量上移", command=lambda: self.batch_move(-1)).pack(side=tk.LEFT, padx=3, pady=5)
        ttk.Button(batch, text="批量下移", command=lambda: self.batch_move(1)).pack(side=tk.LEFT, padx=3, pady=5)

        self.txt = None  # 用于提示

    def update_author_category(self, *_args):
        if self.var_cat.get() == "作者推荐":
            if not self.var_author_cat.get():
                self.var_author_cat.set(AUTHOR_CATEGORIES[0])
            self.author_cat_label.grid()
            self.author_cat_combo.grid()
        else:
            self.author_cat_label.grid_remove()
            self.author_cat_combo.grid_remove()

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

    def selected_indices(self):
        return sorted(int(iid) for iid in self.tree.selection())

    def require_selection(self):
        indices = self.selected_indices()
        if not indices:
            messagebox.showwarning("提示", "请先在表格里选中至少一条记录")
        return indices

    def on_select(self, _event=None):
        sel = self.selected_indices()
        if len(sel) != 1:
            self.cur_index = None
            return
        idx = sel[0]
        self.cur_index = idx
        it = self.items[idx]
        self._loading = True
        self.var_title.set(it.get("title", ""))
        self.var_author.set(it.get("author", ""))
        self.var_cat.set(it.get("category", "") or CATEGORIES[0])
        self.var_author_cat.set(it.get("authorCategory", "") or AUTHOR_CATEGORIES[0])
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
        self.var_author_cat.set(AUTHOR_CATEGORIES[0])
        self.txt_desc.delete("1.0", tk.END)

    # ---------- 表单 -> dict ----------
    def form_dict(self):
        item = {
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
        if item["category"] == "作者推荐":
            item["authorCategory"] = self.var_author_cat.get()
        return item

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
        if self.cur_index is None or self.selected_indices() != [self.cur_index]:
            messagebox.showwarning("提示", "请先只选中一条记录；多条请使用批量编辑")
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
        if self.cur_index is None or self.selected_indices() != [self.cur_index]:
            messagebox.showwarning("提示", "请先只选中一条记录；多条请使用批量删除")
            return
        title = self.items[self.cur_index].get("title", "")
        if not messagebox.askyesno("确认删除", f"确定删除「{title}」？"):
            return
        del self.items[self.cur_index]
        self.clear_form()
        self._persist()

    def move(self, step):
        if self.cur_index is None or self.selected_indices() != [self.cur_index]:
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

    def batch_edit(self):
        indices = self.require_selection()
        if not indices:
            return
        win = tk.Toplevel(self.root)
        win.title(f"批量编辑 · {len(indices)} 条")
        win.geometry("560x570")
        win.transient(self.root)
        win.grab_set()
        ttk.Label(win, text="勾选要修改的字段；未勾选的保持原值，勾选后留空可清空可选字段。",
                  wraplength=520).pack(anchor="w", padx=12, pady=(12, 8))
        form = ttk.Frame(win)
        form.pack(fill=tk.BOTH, expand=True, padx=12)
        form.columnconfigure(1, weight=1)
        fields = [
            ("title", "标题"), ("cover", "封面链接"), ("author", "作者"),
            ("category", "分类"), ("authorCategory", "作者分类"),
            ("gameVer", "版本"), ("tags", "标签"), ("link", "网盘链接"),
            ("code", "提取码"), ("desc", "详细介绍"),
        ]
        checks, values = {}, {}
        for row, (key, label) in enumerate(fields):
            checks[key] = tk.BooleanVar(value=False)
            ttk.Checkbutton(form, text=label, variable=checks[key]).grid(
                row=row, column=0, sticky="nw", padx=(0, 12), pady=3)
            if key == "desc":
                values[key] = tk.Text(form, height=5, wrap="word")
                values[key].grid(row=row, column=1, sticky="ew", pady=3)
            else:
                values[key] = tk.StringVar()
                if key in ("category", "authorCategory"):
                    choices = CATEGORIES if key == "category" else AUTHOR_CATEGORIES
                    widget = ttk.Combobox(form, textvariable=values[key], values=choices,
                                          state="readonly")
                else:
                    widget = ttk.Entry(form, textvariable=values[key])
                widget.grid(row=row, column=1, sticky="ew", pady=3)

        def apply():
            updates = {}
            for key, _ in fields:
                if not checks[key].get():
                    continue
                value = (values[key].get("1.0", tk.END) if key == "desc"
                         else values[key].get()).strip()
                if key in ("title", "category", "authorCategory") and not value:
                    messagebox.showwarning("提示", f"勾选的{dict(fields)[key]}不能为空", parent=win)
                    return
                updates[key] = split_tags(value) if key == "tags" else value
            if not updates:
                messagebox.showwarning("提示", "请先勾选要修改的字段", parent=win)
                return
            if ("authorCategory" in updates and "category" not in updates
                    and any(self.items[i]["category"] != "作者推荐" for i in indices)):
                messagebox.showwarning("提示", "作者分类只适用于作者推荐，请先统一分类", parent=win)
                return
            if "authorCategory" in updates and updates.get("category") not in (None, "作者推荐"):
                messagebox.showwarning("提示", "作者分类只适用于作者推荐", parent=win)
                return
            for idx in indices:
                item = self.items[idx]
                item.update({k: v for k, v in updates.items() if k != "authorCategory"})
                if item["category"] == "作者推荐":
                    if "authorCategory" in updates:
                        item["authorCategory"] = updates["authorCategory"]
                    else:
                        item.setdefault("authorCategory", AUTHOR_CATEGORIES[0])
                else:
                    item.pop("authorCategory", None)
            if self._persist():
                self.tree.selection_set(*(str(i) for i in indices))
                self.cur_index = None
                win.destroy()

        ttk.Button(win, text="应用到选中条目", command=apply).pack(pady=10)

    def batch_delete(self):
        indices = self.require_selection()
        if not indices:
            return
        if not messagebox.askyesno("确认批量删除", f"确定删除选中的 {len(indices)} 条记录？"):
            return
        for idx in reversed(indices):
            del self.items[idx]
        self.cur_index = None
        self._persist()

    def batch_move(self, step):
        indices = self.require_selection()
        if not indices:
            return
        selected = set(indices)
        order = indices if step < 0 else reversed(indices)
        changed = False
        for idx in order:
            target = idx + step
            if 0 <= target < len(self.items) and target not in selected:
                self.items[idx], self.items[target] = self.items[target], self.items[idx]
                selected.remove(idx)
                selected.add(target)
                changed = True
        if changed and self._persist():
            self.tree.selection_set(*(str(i) for i in sorted(selected)))
            self.tree.see(str(min(selected)))
            self.cur_index = None

    def copy_json(self):
        if self.cur_index is None or self.selected_indices() != [self.cur_index]:
            messagebox.showwarning("提示", "请先只选中一条记录")
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
