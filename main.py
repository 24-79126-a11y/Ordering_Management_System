"""Desktop application entry point."""

import tkinter as tk

from ui import OrderingApp


def main() -> None:
    root = tk.Tk()
    OrderingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()