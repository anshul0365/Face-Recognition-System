from flask import Flask, request, redirect, url_for, flash, send_file
from flask.helpers import send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

import os
import base64
from PIL import Image
from io import BytesIO, StringIO
import numpy as np
import cv2
import io
import re

app = Flask(__name__)
CORS(app)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = './dataset'

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/saveImage', methods=['POST'])
@cross_origin()
def save_image():
    print('inside save_image')
    if request.method == 'POST':
        # print('inside if block')
        # print(os.getcwd())
        if 'imageData' not in request.values:
            return 'No file selected'

        # Collecting base64 data
        imageBase64File = request.values['imageData']

        # count of number of files existing in the specified dir
        imageCount = str(len(os.listdir('./dataset'))+1)
        
        # image_data = re.sub('^data:image/.+;base64,', '', imageBase64File)
        
        # Removing pre-attached un-useful data from base64 data
        image_data = imageBase64File.split('base64,')
        
        # Converting processed base64 data to byte with utf-8 encoding
        arr = bytes(image_data[1], 'utf-8')
        
        # Decoding base64 data to image file
        imageDecoded = Image.open(io.BytesIO(base64.decodebytes(arr)))

        # Saving decoded image file locally
        # print(imageDecoded)
        # imageDecoded.save(os.path.join(
        #     app.config['UPLOAD_FOLDER'], imageCount+'.png'), 'PNG') 
        path = './dataset/'+imageCount+'.png'
        imageDecoded.save(path, 'png')

        # imageDecoded.close()

        # with open("imageToSave.png", "wb") as fh:
        #     fh.write(base64.decodebytes(arr))
        return imageBase64File
    else:
        return 'File not Saved'
        


@app.errorhandler(404)
def page_not_found(e):
    return "Page NOT Found"

if __name__ =='__main__':  
    app.run(debug = True) 
