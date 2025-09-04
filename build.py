import os
import zipfile
import shutil

def build_game_package():
    # Create dist directory if it doesn't exist
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # List of files/folders to include in the package
    files_to_include = [
        'main.py',
        'config.py',
        'sprites.py',
        'fonts',
        'Food',
        'Treasure',
        'img',
        'level_graphics',
        'README.md'  # Create this file if it doesn't exist
    ]
    
    # Create a zip file
    with zipfile.ZipFile('dist/adventure_game.zip', 'w') as zipf:
        for item in files_to_include:
            if os.path.isfile(item):
                zipf.write(item, os.path.basename(item))
            elif os.path.isdir(item):
                for root, _, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, file_path)
    
    print("Game package created at 'dist/adventure_game.zip'")

if __name__ == "__main__":
    build_game_package()
