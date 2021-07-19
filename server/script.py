from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS, cross_origin
from flask.wrappers import Response

import io
import os
import cv2
import time
import shutil
import pickle
import base64
import imutils
import argparse
from PIL import Image
import face_recognition
from imutils.video import VideoStream
from imutils import paths

app = Flask(__name__)
CORS(app)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = './dataset'

@app.route('/')
def home():
    return url_for("../client/index.html")

@app.route('/recognize')
def recognize():
    return render_template('recognize.html')

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
            return jsonify(statusText="success", status=200, message="Face Data Saved Successfully")
    else:
        return jsonify(statusText="fail", status=400, message="Directory not present. Try again later")

@app.route('/encode_face', methods=['POST'])
@cross_origin()
def encode_face():

    # USAGE
    # python encode_faces.py --dataset dataset --encodings encodings.pickle

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--dataset", type=str, default="dataset", help="path to input directory of faces + images")
    ap.add_argument("-e", "--encodings", type=str, default="encodings.pickle", help="path to serialized db of facial encodings")
    ap.add_argument("-d", "--detection-method", type=str, default="hog", help="face detection model to use: either `hog` or `cnn`")
    args = vars(ap.parse_args())

    # grab the paths to the input images in our dataset
    print("[INFO] quantifying faces...")
    imagePaths = list(paths.list_images(args["dataset"]))

    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        # load the input image and convert it from RGB (OpenCV ordering) to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb, model=args["detection_method"])

        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

    # dump the facial encodings + names to disk
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}

    try:
        f = open(args["encodings"], "wb")
        f.write(pickle.dumps(data))
        return jsonify(statusText="success", status=200, message="Encoding successfull")
    except Exception as e:
        print (e)
        return jsonify(statusText="fail", status=400, message="Encoding failed")
    finally:
        f.close()

# Global Variables
vs = None #VideoStream Object
writer = None # Initializing writer varibale to NONE

def recognize():

    # USAGE
    # python recognize_faces_video.py --encodings encodings.pickle
    # python recognize_faces_video.py --encodings encodings.pickle --output output/jurassic_park_trailer_output.avi --display 0

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--encodings", default="encodings.pickle", help="path to serialized db of facial encodings")
    ap.add_argument("-o", "--output", type=str, help="path to output video")
    ap.add_argument("-y", "--display", type=int, default=1, help="whether or not to display output frame to screen")
    ap.add_argument("-d", "--detection-method", type=str, default="hog", help="face detection model to use: either `hog` or `cnn`")
    args = vars(ap.parse_args())

    # load the known faces and embeddings
    print("[INFO] loading encodings...")
    data = pickle.loads(open(args["encodings"], "rb").read())

    # initialize the video stream and pointer to output video file, then
    # allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    # vs = VideoStream(src=0).start()
    global vs
    vs = VideoStream(src=0).start()
    global writer
    # writer = None
    time.sleep(2.0)

    # loop over frames from the video file stream
    while True:
        # grab the frame from the threaded video stream
        frame = vs.read()

        # convert the input frame from BGR to RGB then resize it to have a width of 750px (to speedup processing)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(frame, width=750)
        r = frame.shape[1] / float(rgb.shape[1])

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input frame, then compute
        # the facial embeddings for each face
        boxes = face_recognition.face_locations(rgb, model=args["detection_method"])
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)

        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # rescale the face coordinates
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)

            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        # if the video writer is None *AND* we are supposed to write
        # the output video to disk initialize the writer
        if writer is None and args["output"] is not None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 20, (frame.shape[1], frame.shape[0]), True)

        # if the writer is not None, write the frame with recognized faces to disk
        if writer is not None:
            writer.write(frame)

        # check to see if we are supposed to display the output frame to the screen
        if args["display"] > 0:
            retval, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()

    # check to see if the video writer point needs to be released
    if writer is not None:
        writer.release()

@app.route('/liveStream')
@cross_origin()
def liveStream():
    return Response(recognize(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stopStream', methods=['POST'])
@cross_origin()
def stopStream():
    try:
        global vs
        global writer
        vs.stop()
        vs.stream.release()
        cv2.VideoCapture().release
        writer.release()
        cv2.destroyAllWindows()
        
        return jsonify(statusText="success", status=200, message="Stream Closed")
    except Exception as e:
        return jsonify(statusText="fail", status=400, message=str(e))


@app.route('/clean_up', methods=['POST'])
@cross_origin()
def clean_up():
    try: 
        pass
        # Check if temp folder exists inside dataset, then delete it
        if os.path.isdir('./dataset/temp'):
            shutil.rmtree('./dataset/temp', ignore_errors=True)
            print("clean up successfull")
        return jsonify(statusText="success", status=200, message="Clean Up successfull")
    except Exception as e:
        print (e)
        return jsonify(statusText="fail", status=400, message=str(e))


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(statusText="fail", status=400, message="Bad Request")

if __name__ =='__main__':  
    app.run(debug = True) 
