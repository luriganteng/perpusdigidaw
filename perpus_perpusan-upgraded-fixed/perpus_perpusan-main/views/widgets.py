import tkinter as tk
from tkinter import ttk

COLORS = {
    "bg":         "#F0F4F8",
    "sidebar":    "#1A3C5E",
    "accent":     "#E8A020",
    "accent_d":   "#C4841A",
    "card":       "#FFFFFF",
    "text":       "#1C2B3A",
    "text_muted": "#6B7E8F",
    "danger":     "#D94040",
    "success":    "#2E9E5E",
    "warning":    "#E07B1A",
    "border":     "#D0DCE8",
    "header":     "#12263D",
    "row_alt":    "#F7FAFC",
}

FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_LABEL = ("Segoe UI", 10)
FONT_BTN   = ("Segoe UI", 10, "bold")


def page_header(parent, title, subtitle=""):
    hdr = tk.Frame(parent, bg=COLORS["card"],
                   highlightbackground=COLORS["border"],
                   highlightthickness=1)
    hdr.pack(fill="x", padx=0, pady=0)
    inner = tk.Frame(hdr, bg=COLORS["card"])
    inner.pack(fill="x", padx=24, pady=14)
    tk.Label(inner, text=title, font=FONT_HEAD,
             bg=COLORS["card"], fg=COLORS["sidebar"]).pack(anchor="w")
    if subtitle:
        tk.Label(inner, text=subtitle, font=FONT_SMALL,
                 bg=COLORS["card"], fg=COLORS["text_muted"]).pack(anchor="w")
    return hdr


def card(parent, **kwargs):
    f = tk.Frame(parent, bg=COLORS["card"],
                 highlightbackground=COLORS["border"],
                 highlightthickness=1, **kwargs)
    return f


def stat_card(parent, label, value, color=None, icon=""):
    clr = color or COLORS["sidebar"]
    c = tk.Frame(parent, bg=COLORS["card"],
                 highlightbackground=COLORS["border"],
                 highlightthickness=1)
    inner = tk.Frame(c, bg=COLORS["card"])
    inner.pack(padx=18, pady=14, fill="both", expand=True)
    top = tk.Frame(inner, bg=COLORS["card"])
    top.pack(fill="x")
    tk.Label(top, text=icon, font=("Segoe UI", 20),
             bg=COLORS["card"]).pack(side="left")
    tk.Label(top, text=str(value), font=("Segoe UI", 26, "bold"),
             bg=COLORS["card"], fg=clr).pack(side="right")
    tk.Label(inner, text=label, font=FONT_SMALL,
             bg=COLORS["card"], fg=COLORS["text_muted"],
             anchor="w").pack(fill="x", pady=(4, 0))
    tk.Frame(inner, bg=clr, height=3).pack(fill="x", pady=(8, 0))
    return c


def action_btn(parent, text, command, kind="primary"):
    cfg = {
        "primary":   (COLORS["accent"],   COLORS["accent_d"],  COLORS["text"]),
        "danger":    (COLORS["danger"],    "#B03030",           "#fff"),
        "secondary": (COLORS["border"],    "#B8C8D8",           COLORS["text"]),
        "success":   (COLORS["success"],   "#247A4A",           "#fff"),
        "warning":   (COLORS["warning"],   "#B86018",           "#fff"),
    }
    bg, abg, fg = cfg.get(kind, cfg["primary"])
    btn = tk.Button(parent, text=text, command=command,
                    bg=bg, fg=fg, activebackground=abg, activeforeground=fg,
                    relief="flat", cursor="hand2", font=FONT_BTN,
                    padx=14, pady=6)
    return btn


def labeled_entry(parent, label, var=None, width=30, show=None):
    row = tk.Frame(parent, bg=COLORS["card"])
    tk.Label(row, text=label, font=FONT_LABEL,
             bg=COLORS["card"], fg=COLORS["text"],
             width=18, anchor="w").pack(side="left")
    kwargs = dict(font=FONT_BODY, relief="flat", bd=0,
                  highlightthickness=1,
                  highlightbackground=COLORS["border"],
                  highlightcolor=COLORS["accent"],
                  width=width)
    if var:
        kwargs["textvariable"] = var
    if show:
        kwargs["show"] = show
    ent = tk.Entry(row, **kwargs)
    ent.pack(side="left", ipady=5, padx=(0, 4))
    return row, ent


def labeled_combo(parent, label, values, var=None, width=28):
    row = tk.Frame(parent, bg=COLORS["card"])
    tk.Label(row, text=label, font=FONT_LABEL,
             bg=COLORS["card"], fg=COLORS["text"],
             width=18, anchor="w").pack(side="left")
    combo = ttk.Combobox(row, values=values, state="readonly",
                         font=FONT_BODY, width=width)
    if var:
        combo.configure(textvariable=var)
    combo.pack(side="left")
    return row, combo


def search_bar(parent, on_search, placeholder="Cari..."):
    bar = tk.Frame(parent, bg=COLORS["bg"])
    var = tk.StringVar()
    ent = tk.Entry(bar, textvariable=var, font=FONT_BODY,
                   relief="flat", bd=0,
                   highlightthickness=1,
                   highlightbackground=COLORS["border"],
                   highlightcolor=COLORS["accent"],
                   fg=COLORS["text_muted"], width=30)
    ent.insert(0, placeholder)

    def on_focus_in(e):
        if ent.get() == placeholder:
            ent.delete(0, "end")
            ent.configure(fg=COLORS["text"])

    def on_focus_out(e):
        if not ent.get():
            ent.insert(0, placeholder)
            ent.configure(fg=COLORS["text_muted"])

    ent.bind("<FocusIn>", on_focus_in)
    ent.bind("<FocusOut>", on_focus_out)
    ent.bind("<KeyRelease>", lambda e: on_search(
        "" if ent.get() == placeholder else ent.get()
    ))
    ent.pack(side="left", ipady=6, padx=(0, 6))

    btn = action_btn(bar, "🔍 Cari",
                     lambda: on_search("" if ent.get() == placeholder else ent.get()),
                     kind="secondary")
    btn.pack(side="left")
    return bar, ent


def build_treeview(parent, columns, col_widths=None, height=18):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=COLORS["card"],
                    foreground=COLORS["text"],
                    rowheight=28,
                    fieldbackground=COLORS["card"],
                    font=FONT_BODY)
    style.configure("Custom.Treeview.Heading",
                    background=COLORS["sidebar"],
                    foreground="#FFFFFF",
                    font=("Segoe UI", 10, "bold"),
                    relief="flat")
    style.map("Custom.Treeview",
              background=[("selected", COLORS["accent"])],
              foreground=[("selected", COLORS["text"])])

    frame = tk.Frame(parent, bg=COLORS["card"])
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        height=height, style="Custom.Treeview")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    for col in columns:
        w = (col_widths or {}).get(col, 120)
        tree.heading(col, text=col)
        tree.column(col, width=w, minwidth=60)

    tree.tag_configure("alt", background=COLORS["row_alt"])
    tree.tag_configure("warning", background="#FFF3CD")
    tree.tag_configure("danger", background="#FDECEA")
    tree.tag_configure("success", background="#E8F5E9")
    return frame, tree


def modal(parent, title, width=500, height=540):
    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=COLORS["bg"])
    win.resizable(False, False)
    win.grab_set()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")
    return win


def form_card(parent, title=""):
    c = tk.Frame(parent, bg=COLORS["card"],
                 highlightbackground=COLORS["border"],
                 highlightthickness=1)
    if title:
        tk.Label(c, text=title, font=FONT_HEAD,
                 bg=COLORS["card"], fg=COLORS["sidebar"],
                 anchor="w").pack(fill="x", padx=20, pady=(16, 6))
        tk.Frame(c, bg=COLORS["border"], height=1).pack(fill="x", padx=20)
    return c
