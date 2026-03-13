from flask import Flask, render_template, request,send_from_directory,jsonify,session,redirect,url_for
import os
import json
import os
import io
import zipfile
from flask import send_file

app=Flask(__name__)
app.secret_key='key'

if not os.path.exists('uploads'):
    os.makedirs('uploads')
USER_FILE="user.json"
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    else:
        with open(USER_FILE,'r') as f:
            return json.load(f)
def save_users(users):
    with open(USER_FILE,'w') as f:
        json.dump(users,f)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('register'))
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        users=load_users()

        if username in users:
            return jsonify({'message':'用户名已存在'})
        users[username]=password
        save_users(users)
        return jsonify({'message':'注册成功'})
    else:
        return render_template('register.html')



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        users=load_users()
        if username in users and users[username]==password:
            session['username']=username
            return jsonify({
                "message":"登录成功",
            })
        else:
            return jsonify({'message':'用户名或密码错误'})
    return render_template('login.html')


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

@app.route('/download/<path:file_path>')
def download_file(file_path):
    full_path=os.path.join('uploads',file_path)
    if os.path.isdir(full_path):
        return send_from_directory_zip(full_path,file_path)
    else:
        return send_from_directory('uploads', file_path, as_attachment=True)
def send_from_directory_zip(directory, filename):
    zip_filename=f'{filename}.zip'
    zip_buffer=io.BytesIO()
    with zipfile.ZipFile(zip_buffer,'w',zipfile.ZIP_DEFLATED) as zip_file:
        for root,dirs,files in os.walk(directory):
            for file in files:
                file_path=os.path.join(root,file)
                arcname=os.path.relpath(file_path, os.path.dirname(directory))
                zip_file.write(file_path,arcname=arcname)
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=zip_filename)


@app.route('/files')
def list_files():
    return jsonify(get_dictory_structure('uploads'))
def get_dictory_structure(root_dir):
    structure=[]
    for item in os.listdir(root_dir):
        item_path=os.path.join(root_dir,item)
        if os.path.isdir(item_path):
            structure.append({
                'name':item,
                'type':'folder',
                'path':item_path,
                'children':get_dictory_structure(item_path)
            })
        else:
            structure.append({
                'name':item,
                'type':'file',
                'path':item_path    
            })
    return structure

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
    
@app.route('/upload_folder',methods=['POST'])
def upload_folder():
    file_list=request.files.getlist('upload_folder')
    for file in file_list:
        file_path=os.path.join('uploads',file.filename)
        dictionary=os.path.dirname(file_path)
        if not os.path.exists(dictionary):
            os.makedirs(dictionary)
        file.save(file_path)
    return jsonify({'message':'Folder uploaded successfully'})
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
