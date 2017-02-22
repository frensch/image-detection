import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import detection

app = Flask(__name__)

UPLOAD_FOLDER = './temp'
DB_FOLDER = './static/db'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DB_FOLDER'] = DB_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_db', methods=['POST'])
def upload_file_db():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print 'No file part'
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print 'No selected file'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['DB_FOLDER'], filename))
            detection.load_database()
            return html_image(app.config['DB_FOLDER'] + '/' + filename)
    return upload_page_db()

@app.route('/detect', methods=['POST'])
def detect_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print 'No file part'
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print 'No selected file'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_ret = detection.findMatch(app.config['UPLOAD_FOLDER'] + '/' + filename)
            if image_ret == None:
                return html_not_match()
            return html_image(image_ret)
    return upload_page()

def html_not_match():
    return '<html><head></head><body>It didn\'t match any image!!!</body></html>'

def html_image(filename):
    return '<html><head></head><body><img src=\'./' + filename + '\' height="500" width=250"></body></html>'

@app.route('/', methods=['GET'])
def upload_page():
    return '''
    <html>
<head>
</head>
<body>
    <title>Upload File To Compare</title>
    <h1>Upload File To Compare</h1>
	<form method=post enctype=multipart/form-data action='/detect'>
      <p><input type=file name=file>
         <input type=submit value=Upload>
	</form>
</body>
</html>
    '''

@app.route('/db', methods=['GET'])
def upload_page_db():
    return '''
    <html>
<head>
</head>
<body>
    <title>Upload New Database Image</title>
    <h1>Upload New Database Image</h1>
	<form method=post enctype=multipart/form-data action='/upload_db'>
      <p><input type=file name=file>
         <input type=submit value=Upload>
	</form>
</body>
</html>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)