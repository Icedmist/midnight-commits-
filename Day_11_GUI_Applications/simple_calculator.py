#!/usr/bin/env python3
"""
Simple GUI Calculator
A basic calculator application built with Tkinter.
Features: Addition, subtraction, multiplication, division, and clear functionality.
"""

import tkinter as tk
from tkinter import messagebox


class Calculator:
    """A simple GUI calculator using Tkinter."""

    def __init__(self, root):
        """Initialize the calculator with GUI components."""
        self.root = root
        self.root.title("Simple Calculator")
        self.root.geometry("300x400")
        self.root.resizable(False, False)

        # Expression to evaluate
        self.expression = ""

        # Create display
        self.display = tk.Entry(root, font=('Arial', 20), justify='right', bd=10)
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

        # Button layout
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        # Create buttons
        row = 1
        col = 0
        for button in buttons:
            tk.Button(root, text=button, font=('Arial', 16), command=lambda b=button: self.button_click(b)).grid(
                row=row, column=col, padx=5, pady=5, sticky='nsew'
            )
            col += 1
            if col > 3:
                col = 0
                row += 1

        # Clear button
        tk.Button(root, text='C', font=('Arial', 16), command=self.clear).grid(
            row=row, column=0, columnspan=2, padx=5, pady=5, sticky='nsew'
        )

        # Exit button
        tk.Button(root, text='Exit', font=('Arial', 16), command=root.quit).grid(
            row=row, column=2, columnspan=2, padx=5, pady=5, sticky='nsew'
        )

        # Configure grid weights
        for i in range(6):
            root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)

    def button_click(self, char):
        """Handle button clicks."""
        if char == '=':
            try:
                result = str(eval(self.expression))
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, result)
                self.expression = result
            except:
                messagebox.showerror("Error", "Invalid expression")
                self.clear()
        else:
            self.expression += str(char)
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, self.expression)

    def clear(self):
        """Clear the display and expression."""
        self.expression = ""
        self.display.delete(0, tk.END)


def main():
    """Main function to run the calculator."""
    root = tk.Tk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()