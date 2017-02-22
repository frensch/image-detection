import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import detection

app = Flask(__name__)

UPLOAD_FOLDER = './temp'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            ret = 'image detected: ' + str(detection.findMatch(app.config['UPLOAD_FOLDER'] + '/' + filename))
            return ret
    return upload_page()

@app.route('/', methods=['GET'])
def upload_page():
    return '''
    <html>
<head>
</head>
<body>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
	<form method=post enctype=multipart/form-data action='/detect'>
      <p><input type=file name=file>
         <input type=submit value=Upload>
	</form>
</body>
</html>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)