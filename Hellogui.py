"""
Hello World Animation with tkinter
----------------------------------
- ตัวอักษรตกลงมาแบบเด้ง (bounce) ทีละตัว แล้วลอยเป็นคลื่นพร้อมเปลี่ยนสีรุ้ง
- ดาวกระพริบ, ดาวตก, พลุอัตโนมัติ
- คลิกเมาส์ = จุดพลุ, Space = เล่นใหม่, Esc = ออก
by ekachai

รันด้วย:  python hello_world_animation.py
"""

import tkinter as tk
import tkinter.font as tkfont
import colorsys
import math
import random
import time

W, H = 960, 540
FRAME_MS = 16
TEXT = "Hello, World!"
SUBTITLE = "made with Python + tkinter"
BG_END = (26, 24, 56)  # สีที่อนุภาคจะจางหายไปหา


# ---------- helpers ----------
def hsv(h, s=0.75, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def hex_to_rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(rgb1, rgb2, t):
    t = max(0.0, min(1.0, t))
    return "#%02x%02x%02x" % tuple(int(a + (b - a) * t) for a, b in zip(rgb1, rgb2))


def ease_out_bounce(t):
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


# ---------- app ----------
class HelloWorldApp:
    def __init__(self, root):
        self.root = root
        root.title("Hello, World! ✨")
        root.resizable(False, False)
        self.c = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg="#0f0c29")
        self.c.pack()

        self.draw_gradient()
        self.create_stars()
        self.create_letters()

        self.subtitle = self.c.create_text(
            W / 2, H / 2 + 95, text="", fill="#cfd3ff",
            font=("Consolas", 16, "italic"))
        self.hint = self.c.create_text(
            W / 2, H - 22, text="คลิกเพื่อจุดพลุ  •  Space เล่นใหม่  •  Esc ออก",
            fill="#6c6a9c", font=("Tahoma", 11))

        self.particles = []
        self.meteors = []
        self.next_firework = 2.5
        self.start = time.perf_counter()
        self.last = self.start

        self.c.bind("<Button-1>", lambda e: self.firework(e.x, e.y, 70))
        root.bind("<space>", lambda e: self.restart())
        root.bind("<Escape>", lambda e: root.destroy())

        self.loop()

    # ----- scene setup -----
    def draw_gradient(self):
        top, mid, bot = (15, 12, 41), (48, 43, 99), (36, 36, 62)
        for y in range(0, H, 2):
            t = y / H
            col = mix(top, mid, t * 2) if t < 0.5 else mix(mid, bot, (t - 0.5) * 2)
            self.c.create_rectangle(0, y, W, y + 2, fill=col, outline="")

    def create_stars(self):
        self.stars = []
        for _ in range(140):
            x, y = random.uniform(0, W), random.uniform(0, H)
            r = random.choice([0.8, 1, 1.2, 1.6, 2])
            sid = self.c.create_oval(x - r, y - r, x + r, y + r, fill="white", outline="")
            self.stars.append((sid, random.uniform(0, math.tau), random.uniform(1, 4)))

    def create_letters(self):
        self.font = tkfont.Font(family="Helvetica", size=72, weight="bold")
        widths = [self.font.measure(ch) for ch in TEXT]
        x = (W - sum(widths)) / 2
        self.base_y = H / 2 - 10
        self.letters = []
        for i, (ch, w) in enumerate(zip(TEXT, widths)):
            cx = x + w / 2
            shadow = self.c.create_text(cx + 5, -100, text=ch, font=self.font, fill="#0a0820")
            glow = self.c.create_text(cx + 2, -100, text=ch, font=self.font, fill="#000")
            main = self.c.create_text(cx, -100, text=ch, font=self.font, fill="white")
            self.letters.append({"x": cx, "items": (shadow, glow, main),
                                 "landed": False, "space": ch == " "})
            x += w

    def restart(self):
        self.start = time.perf_counter()
        for L in self.letters:
            L["landed"] = False
        self.c.itemconfigure(self.subtitle, text="")

    # ----- effects -----
    def firework(self, x, y, n=50):
        hue = random.random()
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(1.5, 7)
            r = random.uniform(1.5, 3.2)
            color = hsv(hue + random.uniform(-0.08, 0.08), 0.6, 1)
            pid = self.c.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
            self.particles.append({
                "id": pid, "x": x, "y": y, "r": r,
                "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd,
                "life": 1.0, "decay": random.uniform(0.012, 0.025),
                "rgb": hex_to_rgb(color)})

    def spawn_meteor(self):
        x, y = random.uniform(W * 0.2, W * 1.1), random.uniform(-40, H * 0.3)
        mid = self.c.create_line(x, y, x, y, fill="white", width=2, capstyle=tk.ROUND)
        self.meteors.append({"id": mid, "x": x, "y": y, "life": 1.0})

    # ----- main loop -----
    def loop(self):
        now = time.perf_counter()
        t = now - self.start
        dt = min(now - self.last, 0.05) * 60  # normalise to ~60fps
        self.last = now

        # twinkling stars
        for sid, phase, speed in self.stars:
            v = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(now * speed + phase))
            g = int(255 * v)
            self.c.itemconfigure(sid, fill=f"#{g:02x}{g:02x}{min(255, g + 20):02x}")

        # letters
        n = len(self.letters)
        for i, L in enumerate(self.letters):
            shadow, glow, main = L["items"]
            p = (t - i * 0.09) / 0.9
            if p <= 0:
                y = -100
            elif p < 1:
                y = -100 + (self.base_y + 100) * ease_out_bounce(p)
            else:
                if not L["landed"]:
                    L["landed"] = True
                    if not L["space"]:
                        self.firework(L["x"], self.base_y + 40, 12)
                wave_amp = min(1.0, p - 1) * 14
                y = self.base_y + math.sin(now * 3 + i * 0.55) * wave_amp

            hue = now * 0.12 + i / n
            self.c.coords(main, L["x"], y)
            self.c.coords(glow, L["x"] + 2, y + 2)
            self.c.coords(shadow, L["x"] + 5, y + 6)
            self.c.itemconfigure(main, fill=hsv(hue, 0.55, 1))
            self.c.itemconfigure(glow, fill=hsv(hue + 0.08, 0.9, 0.55))

        # typing subtitle
        intro_end = n * 0.09 + 1.0
        if t > intro_end:
            k = min(len(SUBTITLE), int((t - intro_end) * 22))
            cursor = "▌" if int(now * 2) % 2 == 0 else " "
            self.c.itemconfigure(self.subtitle, text=SUBTITLE[:k] + cursor)

        # auto fireworks
        if t > self.next_firework:
            self.firework(random.uniform(120, W - 120), random.uniform(60, H / 3), 55)
            self.next_firework = t + random.uniform(1.5, 3.2)

        # meteors
        if random.random() < 0.008:
            self.spawn_meteor()
        for m in self.meteors[:]:
            m["x"] -= 14 * dt
            m["y"] += 7 * dt
            m["life"] -= 0.02 * dt
            tail = 90 * m["life"]
            self.c.coords(m["id"], m["x"], m["y"], m["x"] + tail, m["y"] - tail / 2)
            self.c.itemconfigure(m["id"], fill=mix((255, 255, 255), BG_END, 1 - m["life"]))
            if m["life"] <= 0:
                self.c.delete(m["id"])
                self.meteors.remove(m)

        # particles
        for p in self.particles[:]:
            p["vy"] += 0.12 * dt
            p["vx"] *= 0.985
            p["vy"] *= 0.985
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= p["decay"] * dt
            if p["life"] <= 0:
                self.c.delete(p["id"])
                self.particles.remove(p)
                continue
            r = p["r"] * (0.4 + 0.6 * p["life"])
            self.c.coords(p["id"], p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r)
            self.c.itemconfigure(p["id"], fill=mix(p["rgb"], BG_END, 1 - p["life"]))

        self.c.tag_raise(self.hint)
        self.root.after(FRAME_MS, self.loop)


if __name__ == "__main__":
    root = tk.Tk()
    HelloWorldApp(root)
    root.mainloop()