from flask import Flask, render_template, request,send_from_directory,jsonify
import os

app=Flask(__name__)

if not os.path.exists('uploads'):
    os.makedirs('uploads')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload',methods=['POST'])
def receive_file():
    file=request.files['upload_file']
    file.save(os.path.join('uploads',file.filename))
    return jsonify(
        {
            'message':'File uploaded successfully',
            'filename':file.filename
        }
    )
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('uploads',filename,as_attachment=True)


@app.route('/files')
def list_files():
    files=os.listdir('uploads')
    return jsonify(files)

@app.route('/delete/<filename>',methods=['POST'])
def delete_file(filename):
    file_path=os.path.join('uploads',filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify(
            {
                'message':'File deleted successfully',
                'filename':filename
            }
        )
    else:
        return jsonify(
            {
                'message':'File not found',
                'filename':filename
            }
        )
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
