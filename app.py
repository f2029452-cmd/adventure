from flask import Flask, render_template, send_file
import os
import subprocess
from build import build_game_package

app = Flask(__name__)

# Build the game package on startup
if not os.path.exists('dist/adventure_game.zip'):
    build_game_package()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download():
    # Ensure the package exists
    if not os.path.exists('dist/adventure_game.zip'):
        build_game_package()
    return send_file('dist/adventure_game.zip', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
