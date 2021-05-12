from flask import Flask, request
from flask_cors import CORS, cross_origin

import os
import base64
from PIL import Image
import numpy as np
import cv2
import io

app = Flask(__name__)
CORS(app)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = './dataset'

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/getName', methods=['POST'])
@cross_origin()
def getName():
    name = request.values['name']
    return name

@app.route('/saveImage', methods=['POST'])
@cross_origin()
def save_image():
    print('inside save_image')
    if request.method == 'POST':
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

        # Image Path
        path = './dataset/'+imageCount+'.png'

        # Saving decoded image file locally

        # 1. PIL Method
        try:
            imageDecoded.save(path, 'PNG') 
            # Close File Stream
            imageDecoded.close()
            return "File save successfully"
        except OSError as error:
            return "Unsuccessfull\nError: "+error

        # 2. OpenCV Method
        # result = cv2.imwrite(path, np.array(imageDecoded))
        # if result:
        #     return "File saved successfully"
        # else:
        #     return "Unsuccessfull"
        
        # 3. File Stream Method
        # with open("imageToSave.png", "wb") as fh:
        #     fh.write(base64.decodebytes(arr))
    else:
        return 'Unauthorized Request'
        


@app.errorhandler(404)
def page_not_found(e):
    return "Page NOT Found"

if __name__ =='__main__':  
    app.run(debug = True) 
