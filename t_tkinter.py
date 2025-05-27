import tkinter as tk

root = tk.Tk()
root.title("Test Tkinter")

root.geometry("300x500")
root.attributes('-fullscreen', True)
label = tk.Label(root, text="Tkinter funcționează!", font=("Arial", 14))
label.pack(pady=50)

root.mainloop()