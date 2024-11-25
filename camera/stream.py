from flask import Flask, Response, render_template, request, redirect, flash, send_from_directory
from picamera2 import Picamera2
import cv2
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os


app = Flask(__name__)
app.secret_key = "*********"
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'images')
auth = HTTPBasicAuth()

USER_DATA = {
    "admin": "**********"
}
 
@auth.verify_password
def verify(username, password):
    if not (username and password):
        file1 = open("myfile.txt", "a")  # append mode
        file1.write("Accesso non riuscito da "+ request.remote_addr + " il " + str(datetime.datetime.now()) + "\n")
        file1.close()
        return False
    file1 = open("myfile.txt", "a")  # append mode
    file1.write("Accesso effettuato da " + request.remote_addr + " il " + str(datetime.datetime.now()) + "\n")
    file1.close()
    return USER_DATA.get(username) == password
 

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (980, 720)}))
camera.start()


@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
 

@app.route('/video_feed')
#@auth.login_required
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/submit', methods=['POST','GET'])
#@auth.login_required
def submit():
   if request.method == "POST" and request.form['photo'] == 'photo':
        now = str(datetime.datetime.now())
        camera.capture_file("./images/" + now.replace(" ","_") + ".jpg")
        flash('Foto catturata')
        return redirect(request.referrer)


@app.route('/photos', methods=['POST'])
@auth.login_required
def see_photos():
   if request.method == "POST" and request.form['photos'] == 'photos':
        # get the path/directory
        folder_dir = "./images"
        lista = os.listdir(folder_dir)
        if lista != []:
            return render_template('photos.html', lista=lista)
        else:
            return "NO PHOTOS!!"

@app.route('/images/<path:filename>')
@auth.login_required
def media(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port =5000)