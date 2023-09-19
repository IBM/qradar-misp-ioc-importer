from flask import Blueprint, render_template, current_app, send_from_directory, request
from .misp import get_misp_ips, check_ref_set, create_ref_set, post_iocs_to_qradar
import json
import urllib3
import logging
import socket
import time
import threading
import os
import traceback
from flask import jsonify
from qpylib import qpylib

log_filename = "/opt/app-root/store/log/startup.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 

fh = logging.FileHandler(log_filename)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

viewsbp = Blueprint('viewsbp', __name__, url_prefix='/')

MISP_headers = {
    'cache-control': "no-cache",
}

QRadar_headers = {
    'content-type': "application/json",
}

polling_thread = None
polling_thread_lock = threading.Lock()

class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def get_form_data(form, field, default=''):
    data = form.get(field)
    return data if data else default


def set_polling_thread(countdown, misp_server, misp_auth_key, qradar_server, qradar_auth_key, qradar_ref_set, event_id, ioc_type):
    global polling_thread_lock
    with polling_thread_lock:
        global polling_thread
        if polling_thread is not None and polling_thread.is_alive():
            polling_thread.stop()
            polling_thread.join()
        polling_thread = StoppableThread(target=poll_ioc_import, args=(countdown, misp_server, misp_auth_key, qradar_server, qradar_auth_key, qradar_ref_set, event_id, ioc_type))
        polling_thread.start()

@viewsbp.route('/index', methods=['GET', 'POST']) # for QRadar
#@viewsbp.route('/', methods=['GET', 'POST']) # for Local system
def index():
    initial_load = True
    global polling_thread
    logs = []
    debug_logs = read_logs()
    countdown = 0
    misp_auth_key = ''
    misp_server = ''
    qradar_server = ''
    qradar_auth_key = ''
    qradar_ref_set = ''
    event_id = ''
    ioc_type = ''
    polling_interval_minutes = 0
    ioc_list = []

    config_file_path = '/opt/app-root/store/config.json'
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            config = json.load(f)
            misp_auth_key = config.get('misp_auth_key', '')
            misp_server = config.get('misp_server', '')
            qradar_server = config.get('qradar_server', '')
            qradar_auth_key = config.get('qradar_auth_key', '')
            qradar_ref_set = config.get('qradar_ref_set', '')
            polling_interval_minutes = config.get('polling_interval_minutes', 0)
            ioc_list = config.get('ioc_list', [])

    if all([misp_auth_key, misp_server, qradar_server, qradar_auth_key, qradar_ref_set]):
        initial_load = False
        if polling_interval_minutes > 0:
            logs.append(f'Polling interval updated to {polling_interval_minutes} minutes')
            countdown = polling_interval_minutes * 60
            if polling_thread is not None and polling_thread.is_alive():
                polling_thread.stop()
                polling_thread.join()
            polling_thread = StoppableThread(target=poll_ioc_import, args=(countdown, misp_server, misp_auth_key, qradar_server, qradar_auth_key, qradar_ref_set, event_id, ioc_type))
            polling_thread.start()
        else:
            logs.append('Polling is disabled (interval is set to 0)')


    if request.method == 'POST':
        initial_load = False
        if polling_thread is not None and polling_thread.is_alive():
            polling_thread.stop()
            polling_thread.join()

        misp_auth_key = request.form.get('misp_auth_key')
        misp_server = request.form.get('misp_server')
        qradar_server = request.form.get('qradar_server')
        qradar_auth_key = request.form.get('qradar_auth_key')
        qradar_ref_set = request.form.get('qradar_ref_set')
        event_id = request.form.get('event_id') # the 'event_id' should match whatever input name you use in your HTML form
        ioc_type = request.form.get('ioc_type') # same here with 'ioc_type'
        #ioc_list = get_misp_ips(misp_server, misp_auth_key, event_id, ioc_type)
        polling_interval_str = request.form.get('polling_interval', '0')
        polling_interval_minutes = int(polling_interval_str) if polling_interval_str.strip() != '' else 0
        

        logs = []

        try:
            if polling_interval_minutes > 0:
                logs.append(f'Polling interval updated to {polling_interval_minutes} minutes')
                logs.append("Fetching IOCs from MISP server...")
                ioc_list = get_misp_ips(misp_server, misp_auth_key, event_id, ioc_type)
                logs.append(f"Retrieved {len(ioc_list)} IOCs from MISP")

                if ioc_list:
                    logs.append("Posting IOCs to QRadar server...")
                    if not check_ref_set(qradar_server, qradar_auth_key, qradar_ref_set):
                        create_ref_set(qradar_server, qradar_auth_key, qradar_ref_set)
                        logs.append(f"Created reference set {qradar_ref_set} in QRadar")

                    post_iocs_to_qradar(qradar_server, qradar_auth_key, qradar_ref_set, ioc_list)
                    logs.append(f"Posted {len(ioc_list)} IOCs to QRadar")

            else:
                logs.append('Polling is disabled (interval is set to 0)')
                ioc_list = []

            config = {
                'misp_auth_key': misp_auth_key,
                'misp_server': misp_server,
                'qradar_server': qradar_server,
                'qradar_auth_key': qradar_auth_key,
                'qradar_ref_set': qradar_ref_set,
                'polling_interval_minutes': polling_interval_minutes,
                'ioc_list': ioc_list[-10:]  # Only keep the last 10 IOCs
            }


            with open(config_file_path, 'w') as f:
                json.dump(config, f)

            logs.append("Configuration updated")

            if polling_interval_minutes > 0:
                countdown = polling_interval_minutes * 60
                set_polling_thread(countdown, misp_server, misp_auth_key, qradar_server, qradar_auth_key, qradar_ref_set, event_id, ioc_type)

        except Exception as err:
            error_message = f"An error occurred: {err}\n{traceback.format_exc()}"
            logger.error(error_message)
            logs.append(error_message)

    return render_template('index.html',
                            misp_auth_key=misp_auth_key,
                            misp_server=misp_server,
                            qradar_server=qradar_server,
                            qradar_auth_key=qradar_auth_key,
                            qradar_ref_set=qradar_ref_set,
                            polling_interval_minutes=polling_interval_minutes,
                            logs=logs,
                            debug_logs=debug_logs,
                            ioc_list=ioc_list,
                            initial_load=initial_load)


def poll_ioc_import(polling_interval, misp_server, misp_auth_key, qradar_server, qradar_auth_key, qradar_ref_set, event_id, ioc_type):
    page = 1
    while not polling_thread.stopped():  # Check if the thread has been stopped
        try:
            logger.debug("Starting new iteration of poller loop")

            log_message = "Fetching IOCs from MISP server..."
            logger.debug(log_message)
            ioc_list = get_misp_ips(misp_server, misp_auth_key, event_id, ioc_type, page=page)

            if not ioc_list:
                logger.debug("No more IOCs to fetch from MISP. Polling will stop.")
                break

            log_message = f"Retrieved {len(ioc_list)} IOCs from MISP"
            logger.debug(log_message)

            if ioc_list:
                log_message = "Posting IOCs to QRadar server..."
                logger.debug(log_message)

                if not check_ref_set(qradar_server, qradar_auth_key, qradar_ref_set):
                    create_ref_set(qradar_server, qradar_auth_key, qradar_ref_set)
                    logger.debug(f"Created reference set {qradar_ref_set} in QRadar")

                post_iocs_to_qradar(qradar_server, qradar_auth_key, qradar_ref_set, ioc_list)

                log_message = f"Posted {len(ioc_list)} IOCs to QRadar"
                logger.debug(log_message)

            page += 1

            logger.debug("Finished iteration of poller loop")

        except Exception as err:
            error_message = f"An error occurred: {err}"
            logger.error(error_message)

        time_left = polling_interval
        while time_left > 0 and not polling_thread.stopped():  # Check if the thread has been stopped
            log_message = f"Next iteration in {time_left} Seconds..."
            logger.debug(log_message)
            time.sleep(1)
            time_left -= 1

def read_logs():
    if os.path.isfile(log_filename):
        with open(log_filename, 'r') as log_file:
            lines = log_file.readlines()
            last_lines = lines[-10:]  # adjust this number as needed
            return last_lines
    else:
        return ["No log file found."]
