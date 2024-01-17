#!/usr/bin/python3

from falcon.http_status import HTTPStatus
import os
import time
import falcon
import logging
import subprocess
import rapidjson as json
import threading

LOGGER_ = logging.getLogger(__name__)
uploadingThread = None
output = []
errors = []

class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise HTTPStatus(falcon.HTTP_200, body='\n')
        
def upload(env):
    LOGGER_.info("Uploading...")

    loader_process = subprocess.Popen(
        ["make", "test_data"], 
        bufsize=1,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        cwd="/comori-od/web/comori-od-all",
        env=env)
    
    def readStdout():
        for line in loader_process.stdout:
            output.append(line.decode('utf-8').rstrip())
            LOGGER_.info(line.decode('utf-8').rstrip())

    def readStderr():
        for line in loader_process.stderr:
            errors.append(line.decode('utf-8').rstrip())
            LOGGER_.error(line.decode('utf-8').rstrip())

    stdoutThread = threading.Thread(target=readStdout)
    stderrThread = threading.Thread(target=readStderr)

    stdoutThread.start()
    stderrThread.start()

    stdoutThread.join()
    stderrThread.join()

    LOGGER_.info("Waiting for loader process to finish...")
    loader_process.wait()
    LOGGER_.info("done!")

    global uploadingThread
    uploadingThread = None

class Uploader(object):
    def on_get(self, req, resp):
        global uploadingThread, output, errors

        if uploadingThread == None and not output and not errors:
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({'message': 'No uploading task running'})
        else:
            resp.status = falcon.HTTP_200
            resp.text = json.dumps({'output': output, 'errors': errors})
            output = []
            errors = []
            

    def on_post(self, req, resp):
        global uploadingThread
        LOGGER_.info(f"Uploading thread is {uploadingThread}")
        if uploadingThread != None:
            resp.status = falcon.HTTP_403
            resp.text = json.dumps({'message': 'Uploading task already running'})
        else:
            env = os.environ
            data = json.loads(req.stream.read())
            env['API_TOTP_KEY'] = data['API_TOTP_KEY']

            try:
                uploadingThread = threading.Thread(target=upload, args=(env,))
                uploadingThread.start()

                resp.status = falcon.HTTP_200
                resp.text = json.dumps({'message': 'Uploading task started!'})
            except Exception as e:
                message = f"Uploading failed! Error: '{str(e)}'"
                LOGGER_.warning(message, exc_info=True)
                resp.status = falcon.HTTP_500
                resp.text = json.dumps({'message': message})

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    app = falcon.App(middleware=[HandleCORS()])

    uploader = Uploader()

    app.add_route('/upload', uploader)

    return app