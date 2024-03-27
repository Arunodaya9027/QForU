import PyInstaller.__main__
import os

# Specify the path to the main script
script_path = os.path.join('F:/Projects/Extensions/LeetScrap', 'launch.py')
# Specify the output path without the file extension
output_path = os.path.join(
    'F:/Projects/Extensions/LeetScrap/dist', 'leetscrapping')

PyInstaller.__main__.run([
    script_path,
    '--onefile',
    '--windowed',
    '--name=leetscrapping',  # Replace 'name' with the desired name of the executable
    '--distpath=' + output_path,
    '--specpath=' + output_path
])
