#!/usr/bin/env python3
"""
Simple Drawing App
A basic drawing application built with Tkinter.
Features: Draw with mouse, change colors, clear canvas, and save drawings.
"""

import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw


class DrawingApp:
    """A simple drawing application using Tkinter."""

    def __init__(self, root):
        """Initialize the drawing app with GUI components."""
        self.root = root
        self.root.title("Simple Drawing App")
        self.root.geometry("800x600")

        # Drawing parameters
        self.color = 'black'
        self.brush_size = 5
        self.last_x = None
        self.last_y = None

        # Create toolbar
        toolbar = tk.Frame(root, height=50)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Color button
        tk.Button(toolbar, text="Color", command=self.choose_color).pack(side=tk.LEFT, padx=5, pady=5)

        # Brush size
        tk.Label(toolbar, text="Size:").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.IntVar(value=self.brush_size)
        tk.Scale(toolbar, from_=1, to=20, orient=tk.HORIZONTAL, variable=self.size_var,
                command=self.change_size).pack(side=tk.LEFT, padx=5)

        # Clear button
        tk.Button(toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=5, pady=5)

        # Save button
        tk.Button(toolbar, text="Save", command=self.save_drawing).pack(side=tk.LEFT, padx=5, pady=5)

        # Create canvas
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # PIL image for saving
        self.image = Image.new("RGB", (800, 550), "white")
        self.draw = ImageDraw.Draw(self.image)

        # Bind mouse events
        self.canvas.bind('<B1-Motion>', self.draw_line)
        self.canvas.bind('<ButtonRelease-1>', self.reset_last_pos)

    def choose_color(self):
        """Choose drawing color."""
        color = colorchooser.askcolor(title="Choose color")
        if color[1]:
            self.color = color[1]

    def change_size(self, value):
        """Change brush size."""
        self.brush_size = int(value)

    def draw_line(self, event):
        """Draw line on canvas."""
        if self.last_x and self.last_y:
            # Draw on canvas
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                  fill=self.color, width=self.brush_size, capstyle=tk.ROUND)

            # Draw on PIL image
            self.draw.line([self.last_x, self.last_y, event.x, event.y],
                          fill=self.color, width=self.brush_size)

        self.last_x = event.x
        self.last_y = event.y

    def reset_last_pos(self, event):
        """Reset last position when mouse button is released."""
        self.last_x = None
        self.last_y = None

    def clear_canvas(self):
        """Clear the canvas."""
        self.canvas.delete('all')
        self.image = Image.new("RGB", (800, 550), "white")
        self.draw = ImageDraw.Draw(self.image)

    def save_drawing(self):
        """Save the drawing as an image file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"),
                                                          ("JPEG files", "*.jpg"),
                                                          ("All files", "*.*")])
        if file_path:
            try:
                self.image.save(file_path)
                messagebox.showinfo("Success", "Drawing saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save drawing: {str(e)}")


def main():
    """Main function to run the drawing app."""
    root = tk.Tk()
    DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()