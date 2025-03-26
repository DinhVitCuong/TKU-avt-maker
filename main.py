import tkinter as tk
from tkinter import ttk, filedialog, font, colorchooser
from PIL import Image, ImageTk, ImageGrab
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class AvatarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TKU Avatar Maker")

        self.canvas = tk.Canvas(root, width=500, height=500, bg='white')
        self.canvas.pack()

        self.base_thumbs = []
        self.tk_img = None
        self.img_id = None
        self.stickers = []
        self.selected_sticker = None
        self.base_img_path = None

        self.setup_ui()
        self.setup_trashbin()

    def setup_ui(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Upload Image", command=self.upload_image).pack(side="left")
        tk.Button(btn_frame, text="Use Base Image", command=self.use_base_image).pack(side="left")
        tk.Button(btn_frame, text="Add Sticker", command=self.open_sticker_gallery).pack(side="left")
        tk.Button(btn_frame, text="Add Text", command=self.add_text_layer).pack(side="left")
        tk.Button(btn_frame, text="Save Avatar", command=self.save_avatar).pack(side="left")

        self.rotation_slider = tk.Scale(btn_frame, from_=0, to=360, orient="horizontal", label="Rotate", command=self.rotate_selected_sticker)
        self.rotation_slider.pack(side="left")

        self.resize_slider = tk.Scale(btn_frame, from_=10, to=300, orient="horizontal", label="Resize", command=self.resize_selected_sticker)
        self.resize_slider.pack(side="left")

        self.root.bind("<Delete>", self.delete_selected_sticker)
        self.canvas.bind("<Button-1>", self.select_canvas_item)
        self.canvas.bind("<B1-Motion>", self.drag_canvas_item)

        layer_frame = tk.Frame(self.root)
        layer_frame.pack(side="right", fill="y")

        tk.Label(layer_frame, text="Layers").pack()

        self.layer_tree = ttk.Treeview(layer_frame, columns=("name",), show="headings", height=20)
        self.layer_tree.heading("name", text="Layer")
        self.layer_tree.pack(padx=5, pady=5)

        btns = tk.Frame(layer_frame)
        btns.pack()

        tk.Button(btns, text="↑", command=self.bring_layer_up).pack(fill="x")
        tk.Button(btns, text="↓", command=self.send_layer_down).pack(fill="x")
        tk.Button(btns, text="❌ Delete", command=self.delete_layer).pack(fill="x")
        tk.Button(btns, text="👁 Toggle", command=self.toggle_visibility).pack(fill="x")

        self.layer_tree.bind("<<TreeviewSelect>>", self.select_layer_from_tree)
        # Add this inside setup_ui()
        tk.Label(btn_frame, text="Font").pack(side="left")
        self.font_var = tk.StringVar()
        available_fonts = list(font.families())
        available_fonts.sort()
        self.font_color = "#000000"  # default black
        tk.Button(btn_frame, text="Pick Color", command=self.pick_font_color).pack(side="left")
        self.font_box = ttk.Combobox(btn_frame, textvariable=self.font_var, values=available_fonts, state="readonly", width=15)
        self.font_box.set("Arial")  # Default
        self.font_box.pack(side="left")

    def setup_trashbin(self):
        trash_path = os.path.join(BASE_DIR, "assets", "trash.png")
        if os.path.exists(trash_path):
            self.trash_img = ImageTk.PhotoImage(Image.open(trash_path).resize((50, 50)))
            self.trash_id = self.canvas.create_image(450, 450, image=self.trash_img)
        else:
            self.trash_id = None

    def use_base_image(self):
        gallery = tk.Toplevel(self.root)
        gallery.title("Choose a Base Image")

        frame = tk.Frame(gallery)
        frame.pack()

        asset_folder = os.path.join(BASE_DIR, "assets", "base")
        self.base_thumbs = []

        for filename in os.listdir(asset_folder):
            if filename.endswith(".png"):
                full_path = os.path.join(asset_folder, filename)
                img = Image.open(full_path).resize((100, 100))
                thumb = ImageTk.PhotoImage(img)
                self.base_thumbs.append(thumb)
                tk.Button(frame, image=thumb, command=lambda p=full_path: self.select_image(p, gallery)).pack(side="left", padx=5, pady=5)

    def select_image(self, path, window=None):
        self.base_img_path = path
        self.tk_img = ImageTk.PhotoImage(Image.open(path).resize((200, 200)))
        if self.img_id:
            self.canvas.delete(self.img_id)
        self.img_id = self.canvas.create_image(250, 250, image=self.tk_img)
        if window:
            window.destroy()

    def upload_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.select_image(path)

    def open_sticker_gallery(self):
        gallery = tk.Toplevel(self.root)
        gallery.title("Choose a Sticker")
        frame = tk.Frame(gallery)
        frame.pack()
        folder = os.path.join(BASE_DIR, "assets", "sticker")
        self.sticker_thumbs = []
        for filename in os.listdir(folder):
            if filename.endswith(".png"):
                full_path = os.path.join(folder, filename)
                img = Image.open(full_path).resize((80, 80))
                thumb = ImageTk.PhotoImage(img)
                self.sticker_thumbs.append(thumb)
                tk.Button(frame, image=thumb, command=lambda p=full_path: self.add_sticker(p, gallery)).pack(side="left")

    def add_sticker(self, path, window=None):
        img = Image.open(path)
        tk_img = ImageTk.PhotoImage(img)
        sticker_id = self.canvas.create_image(250, 250, image=tk_img)
        sticker = {'id': sticker_id, 'image': tk_img, 'path': path, 'angle': 0, 'size': 100, 'visible': True, 'type': 'image'}
        self.stickers.insert(0, sticker)
        self.selected_sticker = sticker_id
        self.layer_tree.insert("", 0, iid=str(sticker_id), values=(os.path.basename(path),))
        if window:
            window.destroy()
    def pick_font_color(self):
        color = colorchooser.askcolor(initialcolor=self.font_color)[1]
        if color:
            self.font_color = color
            # Apply to selected text layer if active
            for s in self.stickers:
                if s['id'] == self.selected_sticker and s['type'] == 'text':
                    self.canvas.itemconfig(s['id'], fill=color)

    def add_text_layer(self):
        text = tk.simpledialog.askstring("Text", "Enter text:")
        if not text:
            return

        selected_font = self.font_var.get() or "Arial"
        f = font.Font(family=selected_font, size=20, weight="bold")

        text_id = self.canvas.create_text(250, 250, text=text, font=f, fill=self.font_color)
        sticker = {
            'id': text_id,
            'type': 'text',
            'text': text,
            'font': f,
            'font_name': selected_font,
            'size': 20,
            'angle': 0,
            'visible': True
        }

        self.stickers.insert(0, sticker)
        self.selected_sticker = text_id
        self.layer_tree.insert("", 0, iid=str(text_id), values=(f"Text: {text[:10]}",))

    def select_canvas_item(self, event):
        clicked = self.canvas.find_closest(event.x, event.y)[0]
        self.selected_sticker = clicked

    def drag_canvas_item(self, event):
        if self.selected_sticker:
            self.canvas.coords(self.selected_sticker, event.x, event.y)
            if self.trash_id:
                tx, ty = self.canvas.coords(self.trash_id)
                if abs(event.x - tx) < 40 and abs(event.y - ty) < 40:
                    self.delete_selected_sticker()

    def rotate_selected_sticker(self, val):
        val = int(val)
        for s in self.stickers:
            if s['id'] == self.selected_sticker and s['type'] == 'image':
                img = Image.open(s['path']).resize((s['size'], s['size']))
                rotated = img.rotate(-val, expand=True)
                s['image'] = ImageTk.PhotoImage(rotated)
                self.canvas.itemconfig(s['id'], image=s['image'])
                s['angle'] = val

    def resize_selected_sticker(self, val):
        val = int(val)
        for s in self.stickers:
            if s['id'] == self.selected_sticker:
                if s['type'] == 'image':
                    img = Image.open(s['path']).resize((val, val))
                    rotated = img.rotate(-s.get('angle', 0), expand=True)
                    s['image'] = ImageTk.PhotoImage(rotated)
                    self.canvas.itemconfig(s['id'], image=s['image'])
                    s['size'] = val
                elif s['type'] == 'text':
                    s['size'] = val
                    f = font.Font(family=s['font_name'], size=val, weight="bold")
                    s['font'] = f
                    self.canvas.itemconfig(s['id'], font=f)


    def delete_selected_sticker(self, event=None):
        if self.selected_sticker:
            self.canvas.delete(self.selected_sticker)
            self.stickers = [s for s in self.stickers if s['id'] != self.selected_sticker]
            self.layer_tree.delete(str(self.selected_sticker))
            self.selected_sticker = None

    def select_layer_from_tree(self, event):
        selected = self.layer_tree.selection()
        if selected:
            self.selected_sticker = int(selected[0])
            for s in self.stickers:
                if s['id'] == self.selected_sticker:
                    if s['type'] == 'image':
                        self.rotation_slider.set(s.get('angle', 0))
                        self.resize_slider.set(s.get('size', 100))
                    elif s['type'] == 'text':
                        self.font_box.set(s.get('font_name', "Arial"))
                        self.resize_slider.set(s.get('size', 20))


    def bring_layer_up(self):
        selected = self.layer_tree.selection()
        if selected:
            sid = int(selected[0])
            self.canvas.tag_raise(sid)

    def send_layer_down(self):
        selected = self.layer_tree.selection()
        if selected:
            sid = int(selected[0])
            self.canvas.tag_lower(sid)

    def delete_layer(self):
        self.delete_selected_sticker()

    def toggle_visibility(self):
        selected = self.layer_tree.selection()
        if selected:
            sid = int(selected[0])
            for s in self.stickers:
                if s['id'] == sid:
                    s['visible'] = not s['visible']
                    self.canvas.itemconfigure(sid, state="normal" if s['visible'] else "hidden")

    def save_avatar(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        final_img = Image.new("RGBA", (canvas_width, canvas_height), "WHITE")

        for item in self.canvas.find_all():
            coords = self.canvas.coords(item)
            img_path = self.get_path_by_item_id(item)

            if img_path:
                try:
                    pil_img = Image.open(img_path).convert("RGBA")

                    # Get size and angle if it's a sticker
                    size = 200
                    angle = 0
                    for s in self.stickers:
                        if s['id'] == item:
                            size = s.get('size', 200)
                            angle = s.get('angle', 0)

                    pil_img = pil_img.resize((size, size))
                    pil_img = pil_img.rotate(-angle, expand=True)

                    x = int(coords[0] - pil_img.width / 2)
                    y = int(coords[1] - pil_img.height / 2)

                    final_img.paste(pil_img, (x, y), pil_img)
                except Exception as e:
                    print(f"Error loading image for item {item}: {e}")

        final_img.save("avatar.png")
        print("✅ Avatar saved as avatar.png (no Ghostscript needed)")



if __name__ == "__main__":
    root = tk.Tk()
    app = AvatarApp(root)
    root.mainloop()
