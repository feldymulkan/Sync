from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os

app = Flask(__name__)

# Function to get files in the specified directory
def get_files_in_directory(directory):
    files = []
    for file_name in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file_name)) and not file_name.startswith('.'):
            files.append(file_name)
    return files

@app.route('/')
def index():
    directory = '/home/cipeng/server1/'  # Specify the directory path
    file_names = get_files_in_directory(directory)
    return render_template('home.html', file_names=file_names)

@app.route('/delete_file', methods=['POST'])
def delete_file():
    directory = '/home/cipeng/server1/'  # Specify the directory path
    file_name = request.form.get('file_path')
    if file_name:
        try:
            os.remove(os.path.join(directory, file_name))
            return redirect(url_for('index'))
        except Exception as e:
            return f'Error deleting file: {str(e)}', 500
    else:
        return 'File path not provided', 400

@app.route('/upload_file', methods=['POST'])
def upload_file():
    directory = '/home/cipeng/server1/'  # Specify the directory path
    file = request.files['file']
    if file:
        try:
            file.save(os.path.join(directory, file.filename))
            return redirect(url_for('index'))
        except Exception as e:
            return f'Error uploading file: {str(e)}', 500
    else:
        return 'File not provided', 400

@app.route('/rename')
def rename_page():
    directory = '/home/cipeng/server1/'  # Specify the directory path
    file_names = get_files_in_directory(directory)
    return render_template('rename.html', file_names=file_names)

@app.route('/rename_file', methods=['POST'])
def rename_file():
    directory = '/home/cipeng/server1/'  # Specify the directory path
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')
    if old_name and new_name:
        try:
            os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
            return redirect(url_for('index'))
        except Exception as e:
            return f'Error renaming file: {str(e)}', 500
    else:
        return 'Both old and new file names are required', 400

@app.route('/download_file/<path:filename>', methods=['GET'])
def download_file(filename):
    directory = '/home/cipeng/server1/'  # Specify the directory path
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8888)
