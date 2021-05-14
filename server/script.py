from flask import Flask, request, redirect
from flask_cors import CORS, cross_origin

import os
import base64
from PIL import Image
import io

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
    if request.method == 'POST':
        if 'imageData' not in request.values:
            return 'No file selected'

        # Collecting base64 data
        imageBase64File = request.values['imageData']
        
        # Removing pre-attached un-useful data from base64 data
        image_data = imageBase64File.split('base64,')
        
        # Converting processed base64 data to byte with utf-8 encoding
        arr = bytes(image_data[1], 'utf-8')
        
        # Decoding base64 data to image file
        imageDecoded = Image.open(io.BytesIO(base64.decodebytes(arr)))

        # Check if temp folder already exists or not; if not then create one
        if not os.path.isdir('./dataset/temp'):
            try:
                os.mkdir('./dataset/temp')
            except OSError as error:
                return "Temporary Folder does not created \nError:- "+error
            else:
                print("Temporary Folder created successfully")
        
        # count of number of files existing in the specified dir
        imageCount = str(len(os.listdir('./dataset/temp/'))+1)
        
        # Image Path
        path = './dataset/temp/'+imageCount+'.png'

        # Saving decoded image file locally
        # 1. PIL Method
        try:
            imageDecoded.save(path, 'PNG') 
            # Close File Stream
            imageDecoded.close()
        except OSError as error:
            return "Unsuccessfull\nError: "+error
        else:
            return "File save successfully"
    else:
        return 'Unrecognized HTTP Request'
        

@app.route('/getName', methods=['POST'])
@cross_origin()
def getName():
    name = request.values['name']
    # Check if temp folder already exists or not; if not then return error and redirect to homepage
    if os.path.isdir('./dataset/temp'):
        dir_name = str.lower(name).replace(" ", "_")
        count = 0
        if any(x.startswith(dir_name) for x in os.listdir('./dataset')):
            count+=1
        try:
            os.rename('./dataset/temp', './dataset/'+dir_name+str(count+1))
        except OSError as error:
            return "Error:- "+error
        else:
            return "Face Data Saved Successfully"
    else:
        return "Directory not present. Try again later" 
        # return redirect('../index.htm')

@app.errorhandler(404)
def page_not_found(e):
    return "Page NOT Found"

if __name__ =='__main__':  
    app.run(debug = True) 
