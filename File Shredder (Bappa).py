import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- SSD detection ---
def is_ssd():
    try:
        return "SSD" in os.popen("wmic diskdrive get model").read().upper()
    except:
        return False

# --- File shredding with wipe method ---
def shred_file_with_method(file_path, method):
    try:
        length = os.path.getsize(file_path)
        with open(file_path, "ba+", buffering=0) as f:
            if method == "0 Overwrite":
                f.seek(0)
                f.write(b"\x00" * length)
            elif method == "Random Overwrite":
                f.seek(0)
                f.write(os.urandom(length))
            elif method == "DoD 5220.22-M":
                for pattern in [b"\x00", b"\xFF"]:
                    f.seek(0)
                    f.write(pattern * length)
                f.seek(0)
                f.write(os.urandom(length))
            elif method == "Gutmann":
                for _ in range(35):
                    f.seek(0)
                    f.write(os.urandom(length))
            elif method == "Schneier":
                for _ in range(7):
                    f.seek(0)
                    f.write(os.urandom(length))
            elif method == "GOST R 50739-95":
                for _ in range(2):
                    f.seek(0)
                    f.write(os.urandom(length))
            else:
                for _ in range(3):
                    f.seek(0)
                    f.write(os.urandom(length))
        os.remove(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed shredding {file_path}:\n{e}")

# --- Add files ---
def add_files():
    files = filedialog.askopenfilenames()
    for f in files:
        file_list.insert(tk.END, f)

# --- Add folder files recursively ---
def add_folder():
    folder = filedialog.askdirectory()
    if not folder:
        return
    for root_dir, _, files in os.walk(folder):
        for name in files:
            file_list.insert(tk.END, os.path.join(root_dir, name))

# --- Shred selected files ---
def shred_selected():
    files = file_list.get(0, tk.END)
    if not files:
        messagebox.showwarning("No files", "Select files first")
        return

    if is_ssd():
        if not messagebox.askyesno("SSD Warning", "SSD detected. Shredding is not 100% secure. Continue?"):
            return

    if not messagebox.askyesno("Confirm", "Permanently delete selected files?"):
        return

    total = len(files)
    progress["maximum"] = total

    for i, f in enumerate(files, start=1):
        shred_file_with_method(f, method_var.get())
        progress["value"] = i
        status_label.config(text=f"Shredding {i}/{total}")
        root.update_idletasks()

    messagebox.showinfo("Done", "Completed")
    file_list.delete(0, tk.END)
    progress["value"] = 0
    status_label.config(text="Idle")

# --- Free space wipe ---
def wipe_free_space():
    folder = filedialog.askdirectory(title="Select folder or drive to wipe free space")
    if not folder:
        return

    if is_ssd():
        if not messagebox.askyesno("SSD Warning", "Free space wipe is unreliable on SSD. Continue?"):
            return

    if not messagebox.askyesno("Confirm", "This will fill free space with junk data. Continue?"):
        return

    temp_file = os.path.join(folder, "wipe_temp.bin")
    max_size = 1024 * 1024 * 1024  # max 1 GB for demo, adjust as needed
    written = 0

    try:
        with open(temp_file, "wb") as f:
            chunk = 1024 * 1024  # 1MB chunks
            while written < max_size:
                f.write(os.urandom(chunk))
                written += chunk
                status_label.config(text=f"Wiping free space: {written // (1024*1024)} MB")
                root.update_idletasks()
    except Exception:
        # Assume disk full or error, stop writing
        pass

    try:
        os.remove(temp_file)
    except:
        pass

    messagebox.showinfo("Done", "Free space wiped")
    status_label.config(text="Idle")

# --- Full disk wipe ---
def wipe_disk():
    drive = filedialog.askdirectory(title="Select DRIVE or folder to wipe (EXTREME DANGER)")
    if not drive:
        return

    confirm1 = messagebox.askyesno("WARNING", "This will DESTROY ALL DATA in selected folder/drive. Continue?")
    if not confirm1:
        return

    confirm2 = messagebox.askyesno("FINAL WARNING", "Are you absolutely sure? This CANNOT be undone.")
    if not confirm2:
        return

    if is_ssd():
        if not messagebox.askyesno("SSD Warning", "SSD detected. Wipe is not 100% secure. Continue?"):
            return

    # Gather all files first to know total count
    files_to_wipe = []
    for root_dir, _, files in os.walk(drive):
        for name in files:
            files_to_wipe.append(os.path.join(root_dir, name))

    total = len(files_to_wipe)
    progress["maximum"] = total

    for i, filepath in enumerate(files_to_wipe, start=1):
        shred_file_with_method(filepath, method_var.get())
        progress["value"] = i
        status_label.config(text=f"Wiping file {i}/{total}")
        root.update_idletasks()

    messagebox.showinfo("Done", "Disk wipe completed")
    status_label.config(text="Idle")
    progress["value"] = 0

# --- GUI Setup ---
root = tk.Tk()
root.title("File Shredder (Bappa)")
root.geometry("550x500")
root.configure(bg="#1e1e1e")
root.resizable(True, True)

style = ttk.Style()
style.theme_use("default")

file_list = tk.Listbox(root, bg="#2b2b2b", fg="white")
file_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

frame = tk.Frame(root, bg="#1e1e1e")
frame.pack()

tk.Button(frame, text="Add Files", command=add_files, bg="#444", fg="white").grid(row=0, column=0, padx=5)
tk.Button(frame, text="Add Folder", command=add_folder, bg="#444", fg="white").grid(row=0, column=1, padx=5)

method_var = tk.StringVar(value="Random Overwrite")
methods = [
    "0 Overwrite",
    "Random Overwrite",
    "DoD 5220.22-M",
    "Gutmann",
    "Schneier",
    "GOST R 50739-95"
]
method_menu = tk.OptionMenu(root, method_var, *methods)
method_menu.config(bg="#444", fg="white")
method_menu.pack(pady=5)

progress = ttk.Progressbar(root, length=500)
progress.pack(pady=10)

status_label = tk.Label(root, text="Idle", bg="#1e1e1e", fg="lightgreen")
status_label.pack()

tk.Button(root, text="Shred Files", bg="red", fg="white", command=shred_selected).pack(pady=5)
tk.Button(root, text="Wipe Free Space", bg="orange", fg="black", command=wipe_free_space).pack(pady=5)
tk.Button(root, text="FULL DISK WIPE (DANGER)", bg="black", fg="white", command=wipe_disk).pack(pady=10)

root.mainloop()
