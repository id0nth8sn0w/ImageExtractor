## @file
# BSD 2-Clause License
#
# Copyright (c) 2025, iDHSN
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

import os
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def extract_images_from_file(input_file, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f'The folder {output_folder} has been created.')

    with open(input_file, 'rb') as file:
        data = file.read()

    jpeg_marker = (b'\xFF\xD8', b'\xFF\xD9')
    png_marker = (b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', b'\x49\x45\x4E\x44\xAE\x42\x60\x82')
    bmp_marker = (b'BM',)  # BMP files do not have a clear end marker, and the size of the image is stored in the header

    start_index = 0
    image_count = 0
    found_images = False

    while start_index < len(data):
        # Looking for all possible file beginnings
        jpeg_pos = data.find(jpeg_marker[0], start_index)
        png_pos = data.find(png_marker[0], start_index)
        bmp_pos = data.find(bmp_marker[0], start_index)

        positions = [pos for pos in (jpeg_pos, png_pos, bmp_pos) if pos != -1]

        if not positions:
            break  # Exit the loop if there is no more data

        start_index = min(positions)

        if start_index == jpeg_pos:
            end_index = data.find(jpeg_marker[1], start_index) + 2
            ext = "jpg"
        elif start_index == png_pos:
            end_index = data.find(png_marker[1], start_index) + len(png_marker[1])
            ext = "png"
        elif start_index == bmp_pos:
            if start_index + 6 > len(data):
                break
            size = int.from_bytes(data[start_index + 2:start_index + 6], 'little')
            end_index = start_index + size
            ext = "bmp"
        else:
            break  # If somehow the file type couldn't be determined

        if end_index <= start_index or end_index > len(data):
            break  # Prevent going beyond the bounds

        image_count += 1
        output_file = os.path.join(output_folder, f'image_{image_count}.{ext}')
        with open(output_file, 'wb') as img_file:
            img_file.write(data[start_index:end_index])

        print(f'Image {image_count} saved as {output_file}')
        found_images = True
        start_index = end_index

    if not found_images:
        print("No images found.")

# Ask the user to select a file
Tk().withdraw()  # Hide the root Tk window
input_file = askopenfilename(title="Select the input file", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])

# Specify the output folder
output_folder = 'output_images'

# Call the function with the selected file
if input_file:
    extract_images_from_file(input_file, output_folder)
else:
    print("No file selected.")

# Wait for any key press before exiting (cross-platform)
if sys.platform == "win32":
    import msvcrt
    print("Press any key to exit...")
    msvcrt.getch()  # Wait for any key press
else:
    import termios
    import tty
    print("Press any key to exit...")
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
