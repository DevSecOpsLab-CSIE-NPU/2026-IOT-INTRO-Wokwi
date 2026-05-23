import subprocess
import sys
import os
import time
try:
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk
except Exception as e:
    print('Missing GUI dependencies:', e)
    sys.exit(1)

THIS_DIR = os.path.dirname(__file__)
RENDER_SCRIPT = os.path.join(THIS_DIR, 'render_oled.py')
OUT_IMG = os.path.join(THIS_DIR, '..', 'oled_screenshot.png')


class TempSliderApp:
    def __init__(self, root):
        self.root = root
        root.title('OLED Temperature Controller')

        self.temp_var = tk.DoubleVar(value=24.0)

        frm = ttk.Frame(root, padding=10)
        frm.grid()

        ttk.Label(frm, text='Temperature (C)').grid(column=0, row=0, sticky='w')
        self.scale = ttk.Scale(frm, from_=0.0, to=50.0, orient='horizontal', variable=self.temp_var, command=self.on_slide)
        self.scale.grid(column=0, row=1, sticky='we')

        self.temp_label = ttk.Label(frm, text='24.0 C')
        self.temp_label.grid(column=0, row=2)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(column=0, row=3, pady=6)
        self.render_btn = ttk.Button(btn_frame, text='Render', command=self.render_once)
        self.render_btn.grid(column=0, row=0, padx=4)
        self.auto_var = tk.BooleanVar(value=True)
        self.auto_check = ttk.Checkbutton(btn_frame, text='Auto', variable=self.auto_var)
        self.auto_check.grid(column=1, row=0)

        self.canvas = tk.Canvas(frm, width=128, height=128, bg='black')
        self.canvas.grid(column=0, row=4, pady=8)

        self.imgtk = None
        self.render_once()

    def on_slide(self, _=None):
        t = self.temp_var.get()
        self.temp_label.config(text='{:.1f} C'.format(t))
        if self.auto_var.get():
            # debounce rapid moves
            self.root.after_cancel(getattr(self, '_after_id', ''))
            self._after_id = self.root.after(300, self.render_once)

    def render_once(self):
        t = self.temp_var.get()
        cmd = [sys.executable, RENDER_SCRIPT, '{:.1f}'.format(t)]
        try:
            subprocess.run(cmd, check=True, cwd=os.path.dirname(THIS_DIR))
        except subprocess.CalledProcessError as e:
            print('Render failed:', e)
            return
        # give filesystem a moment
        time.sleep(0.1)
        if os.path.exists(OUT_IMG):
            try:
                img = Image.open(OUT_IMG).convert('1')
                img = img.resize((256,256), Image.NEAREST)
                self.imgtk = ImageTk.PhotoImage(img)
                self.canvas.create_image(0,0,anchor='nw',image=self.imgtk)
            except Exception as e:
                print('Failed to load image:', e)


def main():
    root = tk.Tk()
    app = TempSliderApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
