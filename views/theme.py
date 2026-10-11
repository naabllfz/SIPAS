import tkinter as tk

BG = "#F4F3EA"
WHITE = "#FFFEF8"
NAVY = "#173B35"
BLUE = "#527A3E"
BLUE_DARK = "#3D6330"
INK = "#2C4037"
MUTED = "#77847A"
LINE = "#E1E4D8"
PALE_BLUE = "#EEF2E5"
GREEN = "#477A58"
PALE_GREEN = "#EAF2E6"
AMBER = "#A96335"
PALE_AMBER = "#F9EEE1"
RED = "#B65C54"
PALE_RED = "#F7E8E2"


def page_heading(parent, eyebrow, title, subtitle):
    tk.Label(
        parent, text=eyebrow.upper(), bg=BG, fg=BLUE,
        font=("Segoe UI", 8, "bold")
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        parent, text=title, bg=BG, fg=NAVY,
        font=("Segoe UI", 23, "bold")
    ).pack(anchor="w")

    tk.Label(
        parent, text=subtitle, bg=BG, fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(5, 20))


def panel(parent, padx=20, pady=18):
    return tk.Frame(
        parent, bg=WHITE, padx=padx, pady=pady,
        highlightbackground=LINE, highlightthickness=1
    )


def primary_button(parent, text, command, **kwargs):
    return tk.Button(
        parent, text=text, command=command, bg=BLUE, fg=WHITE,
        activebackground=BLUE_DARK, activeforeground=WHITE,
        relief="flat", bd=0, cursor="hand2",
        font=("Segoe UI", 9, "bold"), padx=17, pady=10,
        **kwargs
    )


def secondary_button(parent, text, command, **kwargs):
    return tk.Button(
        parent, text=text, command=command, bg=WHITE, fg=INK,
        activebackground="#EFF0E7", activeforeground=NAVY,
        relief="solid", bd=1, cursor="hand2",
        font=("Segoe UI", 9, "bold"), padx=15, pady=9,
        **kwargs
    )


def labeled_entry(parent, label, hint="", show=None):
    wrap = tk.Frame(parent, bg=WHITE)

    tk.Label(
        wrap, text=label, bg=WHITE, fg=INK,
        font=("Segoe UI", 9, "bold")
    ).pack(anchor="w", pady=(0, 7))

    entry = tk.Entry(
        wrap, font=("Segoe UI", 10), relief="solid", bd=1,
        highlightthickness=1, highlightbackground=LINE,
        highlightcolor=BLUE, insertbackground=NAVY
    )

    if hint:
        entry.insert(0, hint)
        entry.configure(fg="#929B8F")

        def focus_in(_event):
            if entry.get() == hint:
                entry.delete(0, "end")
                entry.configure(fg=INK)

        def focus_out(_event):
            if not entry.get():
                entry.insert(0, hint)
                entry.configure(fg="#929B8F")

        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)

    if show:
        entry.configure(show=show)

    entry.pack(fill="x", ipady=9)
    return wrap, entry