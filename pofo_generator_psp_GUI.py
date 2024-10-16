import struct
import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Indonesia
# POFO adalah jarak antar offset yang diencrpyt dengan format dibawah ini.
# Pembuatan POF0 disesuaikan dengan offset mana dulu yang muncul (ascending)
# English:
# POFO is the distance between offsets which is encrypted in the format below.
# POF0 generated is adjusted to which offset appears first (ascending)

def out(p, cursor, diff):   #pofo encrpyt logic
    count = 0
    sp = cursor - diff
    if sp <= 0xFC:
        sp = (sp >> 2) | 0x40
        p.write(struct.pack('B', sp))
        count += 1
    elif sp <= 0xFFFC:
        sp = (sp >> 2) | 0x8000
        sp = struct.pack('>H', sp)
        p.write(sp)
        count += 2
    else:
        sp = (sp >> 2) | 0xC0000000
        sp = struct.pack('>I', sp)
        p.write(sp)
        count += 4
    return count

def validate_pof0(f, p):
    f.seek(4, 0)
    pof0_offset = struct.unpack('>I', f.read(4))[0]
    f.seek(pof0_offset, 1)
    word = f.read(4).decode('ascii')
    if word != "POF0":
        print("Invalid POF0 offset")
        return 1
    f.seek(-8, 1)
    len = struct.unpack('>I', f.read(4))[0] + 8
    for i in range(len):
        val1 = struct.unpack('>I', f.read(4))[0]
        val2 = struct.unpack('>I', p.read(4))[0]
        if val1 != val2:
            print(f"Values at position {i} differ, {val1:x} != {val2:x}")
            return 1
    return 0

def make_new_file(p):
    byte_count = 0
    word = b'POF0'
    p.write(word)
    p.write(struct.pack('>I', byte_count))

def generate_pof0(f, p):
    FILE_HEADER = 8
    vertex_offset =[]
    UV_offset=[]
    texture_offset=[]
    texture_count=[]
    all_offset=[]
    temp=0
    temp1=0
    p.seek(0, os.SEEK_END)
    start_pof0=p.tell()
    f.seek(0)
    word = f.read(4).decode('ascii')
    if word != "YOBJ":
        print("Invalid YOBJ file, JBOY header missing")
        return

    pof0_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, POF0 Offset: {pof0_offset}")
    temp = struct.unpack('<I', f.read(4))[0]  # zero
    temp = struct.unpack('<I', f.read(4))[0]  # pof0 offset again
    print(f"Read Offset {f.tell()-4}, POF02 Offset: {temp}")
    if temp != pof0_offset:
        print("Invalid YOBJ file, second pof0 offset different from first")
        return

    f.read(8)  # skip two zeros
    mesh_count = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Mesh Count: {mesh_count}")

    f.read(8)
    cursor = f.tell()
    all_offset.append(FILE_HEADER)
    all_offset.append(f.tell())
    mesh_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Mesh Offset: {mesh_offset}")

    f.seek(-12,1)
    bone_count = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Bone Count: {bone_count}")

    tex_count = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Texture Count: {tex_count}")

    f.read(4)
    temp = cursor
    cursor = f.tell()
    all_offset.append(f.tell())

    bone_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Bone Offset: {bone_offset}")

    temp = cursor
    cursor = f.tell()
    all_offset.append(f.tell())

    texname_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Texture Name Offset: {texname_offset}")

    temp = cursor
    cursor = f.tell()
    all_offset.append(f.tell())

    obj_groupname_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Object Groupname Offset: {obj_groupname_offset}")

    obj_group_count = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Object Group Count: {obj_group_count}")

    f.seek(mesh_offset)

    for i in range(mesh_count):
        description_offset = f.tell();
        print   (f"Object {i} Offset {f.tell()}")
        f.read(12)  # skip two zeros
        temp1 = struct.unpack('<I', f.read(4))[0]
        texture_count.append(temp1)
        print(f"Read Offset {f.tell()-4}, Texture Count: {temp1}")

        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        vertex_offset.append(temp1)
        print(f"Read Offset {f.tell()-4}, Vertex Offset: {temp1}")

        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        texture_offset.append(temp1)
        print(f"Read Offset {f.tell()-4}, Texture Offset: {temp1}")

        f.read(8)
        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        UV_offset.append(temp1)
        print(f"Read Offset {f.tell()-4}, UV Offset: {temp1}")
        f.read(28)

    for i in range(mesh_count):
        print(f"Object {i} More Detail")

        f.seek(vertex_offset[i]+16)
        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        print(f"Read Offset {f.tell()-4}, Vertex Offset 2: {temp1}")

        f.seek(UV_offset[i]+8)
        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        print(f"Read Offset {f.tell()-4}, UV Offset 2: {temp1}")

        f.seek(texture_offset[i]+140)
        mesh_size=[]
        mesh_offset_a=[]
        for j in range(texture_count[i]):
            print(f"Texture: {j}")

            temp1 = struct.unpack('<I', f.read(4))[0]
            mesh_size.append(temp1)
            print(f"Read Offset {f.tell()-4}, Mesh Size: {temp1}")

            temp = cursor
            cursor = f.tell()
            all_offset.append(f.tell())

            temp1 = struct.unpack('<I', f.read(4))[0]
            mesh_offset_a.append(temp1)
            print(f"Read Offset {f.tell()-4}, Texture Offset A: {temp1}")

            temp = cursor
            cursor = f.tell()
            all_offset.append(f.tell())

            temp1 = struct.unpack('<I', f.read(4))[0]
            print(f"Read Offset {f.tell()-4}, Texture Offset B : {temp1}")
            f.read(132)
        print(mesh_offset_a)
        for j in range(texture_count[i]):
            f.seek(mesh_offset_a[j]+20)
            for k in range(mesh_size[j]):
                temp = cursor
                cursor = f.tell()
                all_offset.append(f.tell())

                temp1 = struct.unpack('<I', f.read(4))[0]
                print(f"Read Offset {f.tell()-4}, Texture {j}, Mesh {k} Offset: {temp1}")
                f.read(12)

    #untuk mengurutkan offset setiap data yang sudah dibaca
    all_offset.sort()
    print(all_offset)
    print(len(all_offset))

    #menulis POF0 menggunakan offset yang sudah diurutkan
    for i in range(len(all_offset)-1):
        cursor = all_offset[i+1]
        temp = all_offset[i]
        out(p, cursor, temp)

    end_pof0=p.tell()
    p.seek(0)
    p.read(4)
    pof0_lenght=end_pof0-start_pof0
    p.write(struct.pack('<I', pof0_lenght))

# Fungsi untuk memilih file input
def select_input_file():
    input_path.set(filedialog.askopenfilename(title="Select YOBJ file", filetypes=[("YOBJ files", "*.yobj"), ("All files", "*.*")]))

# Fungsi untuk memilih file output
def select_output_file():
    output_path.set(filedialog.asksaveasfilename(title="Save POF0 file", defaultextension=".pof0", filetypes=[("POF0 files", "*.pof0"), ("All files", "*.*")]))

# Fungsi utama yang dimodifikasi untuk dijalankan dari tombol GUI
def run_conversion():
    infile = input_path.get()
    outfile = output_path.get()

    if not infile or not outfile:
        messagebox.showerror("Error", "Please select both input and output files.")
        return

    try:
        yobj_file = open(infile, "rb")
    except IOError:
        messagebox.showerror("Error", f"Cannot open {infile}")
        return

    try:
        pof0_file = open(outfile, "wb")
    except IOError:
        messagebox.showerror("Error", f"Cannot open {outfile}")
        return
    make_new_file(pof0_file)
    pof0_file.close()
    try:
        pof0_file = open(outfile, "r+b")
    except IOError:
        messagebox.showerror("Error", f"Cannot open {outfile}")
        return

    generate_pof0(yobj_file, pof0_file)
    pof0_file.close()
    yobj_file.close()

    messagebox.showinfo("Success", "POF0 file generated successfully.")

# Setup GUI
root = tk.Tk()
root.title("YOBJ to POF0 Converter")

input_path = tk.StringVar()
output_path = tk.StringVar()

# Layout
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="YOBJ File:").grid(row=0, column=0, sticky="e")
tk.Entry(frame, textvariable=input_path, width=50).grid(row=0, column=1)
tk.Button(frame, text="Browse...", command=select_input_file).grid(row=0, column=2)

tk.Label(frame, text="POF0 Output File:").grid(row=1, column=0, sticky="e")
tk.Entry(frame, textvariable=output_path, width=50).grid(row=1, column=1)
tk.Button(frame, text="Browse...", command=select_output_file).grid(row=1, column=2)

tk.Button(root, text="Convert", command=run_conversion).pack(pady=10)

root.mainloop()
