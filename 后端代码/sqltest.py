import os
import time
import math
import cv2
import numpy as np

from PIL import Image
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from MySqlUtil import MysqlUtil
import random

app = Flask(__name__)

CORS(app, supports_credentials=True)

ALLOWED_EXTENSIONS = {'png', 'jpg'}


FILE_DIR = 'data/temp/'
FILE_EXPIRE_TIME = 3600



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



def save_upload_file(file):

    timestamp = str(int(time.time()))
    filename = timestamp + str(random.randint(00000, 99999)) + '_' + secure_filename(file.filename)
    file_path = os.path.join(FILE_DIR, filename)
    file.save(file_path)
    return filename



@app.route('/predict', methods=['POST'])
def predict():

    if request.files:
        file = request.files['file']
    else:
        return jsonify({'error': '文件格式错误或文件上传失败'})
    if file and allowed_file(file.filename):
        filename = save_upload_file(file)

        result = "苹果"

        userid = request.form.get("userid")
        db = MysqlUtil()
        sql = f'INSERT INTO image VALUES (null,"{str(os.path.join(FILE_DIR, filename))}","{result}","{userid}")'
        imager = db.insert(sql)
        imagetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = f'INSERT INTO log VALUES (null,{userid},(SELECT id FROM image WHERE imagePath="{os.path.join(FILE_DIR, filename)}"),"{imagetime}")'
        logr = db.insert(sql)
        if logr == 1 and imager == 1:
            msg = "添加成功"
        else:
            msg = "添加失败"
        return jsonify({'result': result, 'msg': msg})
    else:
        print(jsonify({'error': '文件格式错误或文件上传失败'}))
        return jsonify({'error': '文件格式错误或文件上传失败'})



@app.route('/login', methods=['GET'])
def login():
    db = MysqlUtil()
    type = request.args.get("type")
    username = request.args.get("username")
    userpassword = request.args.get("password")
    if type == 'user':
        sql = f'SELECT * from user where userName="{username}" and userPassword="{userpassword}"'
        result = db.fetchall(sql)
        if not result:
            msg = '用户不存在或密码错误'
            return jsonify({'error': 1, 'msg': msg, 'data': result})
        else:
            return jsonify({'error': 0, 'msg': '登录成功', 'data': result})
    elif type == 'admin':
        sql = f'SELECT * from admin where adminName="{username}" and adminPassword="{userpassword}"'
        result = db.fetchall(sql)
        if not result:
            msg = '用户不存在或密码错误'
            return jsonify({'error': 1, 'msg': msg, 'data': result})
        else:
            return jsonify({'error': -1, 'msg': '登录成功', 'data': result})



@app.route('/loglist/<int:page>/<int:pagesize>', methods=['GET'])
def loglist(page, pagesize):
    userid = request.args.get('userid')
    db = MysqlUtil()
    csql = f'select count(*) as count from log where userid={userid}'
    logcount = db.fetchone(csql)['count']
    total = math.ceil(logcount / pagesize)

    sql = f'SELECT log.id,imageid,imagepath,imageRec,addTime from log,image where log.userid={userid} and log.imageid=image.id ORDER BY addTime DESC LIMIT {(page - 1) * pagesize},{pagesize}'
    result = db.fetchall(sql)
    for i in result:
        i['imagename'] = os.path.split(i['imagepath'])[1]
    return jsonify({'error': 0, 'msg': '成功', 'data': result, 'total': total})



@app.route('/userlist/search', methods=['GET'])
def userlistSearch():
    db = MysqlUtil()
    key = request.args.get('key')
    value = request.args.get('value')
    page = int(request.args.get('page'))
    size = int(request.args.get('size'))
    csql = f"select count(*) as count from user where {key} like '%{value}%'"
    logcount = db.fetchone(csql)['count']
    total = math.ceil(logcount / size)
    sql = f"SELECT * from user where {key} like '%{value}%' LIMIT {(page - 1) * size},{size}"
    result = db.fetchall(sql)
    return jsonify({'error': 0, 'msg': '成功', 'data': result, 'total': total})



@app.route('/userlist/<int:page>/<int:pagesize>', methods=['GET'])
def userlist(page, pagesize):
    db = MysqlUtil()
    csql = f'select count(*) as count from user'
    logcount = db.fetchone(csql)['count']
    total = math.ceil(logcount / pagesize)

    sql = f'SELECT * from user LIMIT {(page - 1) * pagesize},{pagesize}'
    result = db.fetchall(sql)
    return jsonify({'error': 0, 'msg': '成功', 'data': result, 'total': total})



@app.route('/userdelete/<int:userid>', methods=['GET'])
def userdelete(userid):
    db = MysqlUtil()
    sql = f'DELETE FROM log where userid={userid}'
    logc = db.delete(sql)
    sql = f'DELETE FROM image where userid={userid}'
    imagec = db.delete(sql)
    sql = f'DELETE FROM user where id={userid}'
    userc = db.delete(sql)
    db.close()
    print(jsonify({'error': 0, 'msg': f'删除{logc}条记录,{imagec}个图像,{userc}个用户', 'data': ''}))
    return jsonify({'error': 0, 'msg': f'删除{logc}条记录,{imagec}个图像,{userc}个用户', 'data': ''})



@app.route('/user/findById/<int:id>', methods=['GET'])
def userFindById(id):
    db = MysqlUtil()
    sql = f'SELECT * FROM user where id={id}'
    result = db.fetchone(sql)
    db.close()
    result['checkPass'] = result['userPassword']
    return jsonify({'error': 0, 'data': result})



@app.route('/user/update', methods=['GET'])
def userUpdate():
    db = MysqlUtil()
    id = request.args.get('id')
    username = request.args.get('userName')
    password = request.args.get('userPassword')
    phone = request.args.get('userPhone')
    sql = f'UPDATE user SET userPassword="{password}",userPhone="{phone}" where id={id}'
    db.update(sql)
    return jsonify({'error': 0, 'data': ''})



@app.route('/userregister', methods=['GET'])
def userregister():
    db = MysqlUtil()
    username = request.args.get('name')
    password = request.args.get('password')
    phone = request.args.get('phone')
    sql = f'SELECT * from user where userName="{username}"'
    if db.fetchone(sql):
        return jsonify({'error': 1, 'msg': f'用户名已存在', 'data': ''})
    else:
        sql = f'INSERT INTO user VALUES (null,"{username}","{password}","{phone}")'
        db.insert(sql)
        db.close()
        return jsonify({'error': 0, 'msg': f'{username}注册成功', 'data': ''})



@app.route('/image/<path:imagepath>', methods=['GET'])
def images(imagepath):
    image_data = open(imagepath, 'rb').read()
    response = Response(image_data, mimetype="image/jpeg")
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
