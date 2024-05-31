import os
import argparse
import requests
import datetime
import threading
import time

def get_data(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as exc:
        print(f"Exception occurred: {exc}")
        return None

    if r.status_code != requests.codes.ok:
        print(f"Got error {r.status_code}: {r.text}")
        return None

    return r.json()

def get_antenna_position(base_url):
    return get_data("{}/api/v1/config/antenna".format(base_url))

def get_acoustic_position(base_url):
    return get_data("{}/api/v1/position/acoustic/filtered".format(base_url))

def get_global_position(base_url):
    return get_data("{}/api/v1/position/global".format(base_url))

def get_master_position(base_url):
    return get_data("{}/api/v1/position/master".format(base_url))

def position_fetch_thread(base_url, position_type, data_queue, lock, stop_event):
    fetch_functions = {
        'acoustic': lambda: get_data(f"{base_url}/api/v1/position/acoustic/filtered"),
        'global': lambda: get_data(f"{base_url}/api/v1/position/global"),
        'master': lambda: get_data(f"{base_url}/api/v1/position/master")
    }
    get_position = fetch_functions[position_type]

    while not stop_event.is_set():
        data = get_position()
        timestamp = datetime.datetime.now().strftime("%Y%m%d.%H%M%S%f")
        with lock:
            data_queue.append((timestamp, position_type, data))
        time.sleep(1)  # Adjust the frequency as needed

def data_saving_thread(save_path, data_queue, lock, stop_event):
    while not stop_event.is_set() or data_queue:
        with lock:
            if data_queue:
                timestamp, position_type, data = data_queue.pop(0)
            else:
                continue

        if data:
            file_path = os.path.join(save_path, f'{position_type}_position.txt')
            with open(file_path, 'a') as f:
                if position_type == 'acoustic':
                    f.write(f"{timestamp},{data['x']},{data['y']},{data['z']}\n")
                else:
                    f.write(f"{timestamp},{data['lat']},{data['lon']}\n")

def main():
    parser = argparse.ArgumentParser(description="Fetch and save position data concurrently.")
    parser.add_argument("-u", "--url", help="Base URL to use", type=str, default="https://demo.waterlinked.com")
    parser.add_argument("-s", "--save", help="Save directory", type=str, default="save")
    # parser.add_argument("-n", "--notsave", help="Don't save the recording", action="store_true")
    args = parser.parse_args()

    # if args.notsave:
    #     return

    save_path = os.path.join(args.save, datetime.datetime.now().strftime("%m%d%H%M"))
    os.makedirs(save_path, exist_ok=True)
    
    antenna_position = get_antenna_position(args.url)
    with open(os.path.join(save_path,'antenna_position.txt'),'w') as f:
        f.write(antenna_position.__str__())
    with open(os.path.join(save_path,'acoustic_position.txt'),'w') as f:
        f.write('t,x,y,z\n')
    with open(os.path.join(save_path,'global_position.txt'),'w') as f:
        f.write('t,lat,lon\n')
    with open(os.path.join(save_path,'master_position.txt'),'w') as f:
        f.write('t,lat,lon\n')

    data_queue = []
    lock = threading.Lock()
    stop_event = threading.Event()

    # Start threads for each position type
    threads = []
    for pos_type in ['acoustic', 'global', 'master']:
        thread = threading.Thread(target=position_fetch_thread, args=(args.url, pos_type, data_queue, lock, stop_event))
        threads.append(thread)
        thread.start()

    # Start the saving thread
    saving_thread = threading.Thread(target=data_saving_thread, args=(save_path, data_queue, lock, stop_event))
    threads.append(saving_thread)
    saving_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        stop_event.set()
        for thread in threads:
            thread.join()
        print("All threads have been stopped.")

if __name__ == "__main__":
    main()

# import os
# import argparse
# import json
# import requests
# import datetime
# from pprint import pprint

# def get_data(url):
#     try:
#         r = requests.get(url)
#     except requests.exceptions.RequestException as exc:
#         print("Exception occured {}".format(exc))
#         return None

#     if r.status_code != requests.codes.ok:
#         print("Got error {}: {}".format(r.status_code, r.text))
#         return None

#     return r.json()

# def get_antenna_position(base_url):
#     return get_data("{}/api/v1/config/antenna".format(base_url))

# def get_acoustic_position(base_url):
#     return get_data("{}/api/v1/position/acoustic/filtered".format(base_url))

# def get_global_position(base_url):
#     return get_data("{}/api/v1/position/global".format(base_url))

# def get_master_position(base_url):
#     return get_data("{}/api/v1/position/master".format(base_url))

# def main():
#     parser = argparse.ArgumentParser(description=__doc__)
#     parser.add_argument(
#         "-u",
#         "--url",
#         help = "Base URL to use",
#         type = str,
#         default = "https://demo.waterlinked.com")
#     parser.add_argument(
#         "-s",
#         "--save",
#         help = "Save dir",
#         type = str,
#         default = "save")
#     parser.add_argument(
#         "-n",
#         "--notsave",
#         help = "Don't save the recording",
#         action = "store_true",)
#     args = parser.parse_args()

#     save_path = os.path.join(args.save,datetime.datetime.now().strftime("%m%d%H%M"))
#     os.makedirs(save_path, exist_ok=True)

#     base_url = args.url
#     print("Using base_url: %s" % args.url)
    
#     antenna_position = get_antenna_position(base_url)
    
#     if not args.notsave:
#         with open(os.path.join(save_path,'antenna_position.txt'),'w') as f:
#             f.write(antenna_position.__str__())
#         with open(os.path.join(save_path,'acoustic_position.txt'),'w') as f:
#             f.write('t,x,y,z\n')
#         with open(os.path.join(save_path,'global_position.txt'),'w') as f:
#             f.write('t,lat,lon\n')
#         with open(os.path.join(save_path,'master_position.txt'),'w') as f:
#             f.write('t,lat,lon\n')

#     while True:
#         timestamp = datetime.datetime.now().strftime("%Y%m%d.%H%M%S%f")
#         acoustic_position = get_acoustic_position(base_url)
#         global_position = get_global_position(base_url)
#         master_position = get_master_position(base_url)
        
#         if not args.notsave:
#             if acoustic_position:
#                 with open(os.path.join(save_path,'acoustic_position.txt'),'a') as f:
#                     f.write(f"{timestamp},{acoustic_position['x']},{acoustic_position['y']},{acoustic_position['z']}\n")
#             if global_position:
#                 with open(os.path.join(save_path,'global_position.txt'),'a') as f:
#                     f.write(f"{timestamp},{global_position['lat']},{global_position['lon']}\n")
#             if master_position:
#                 with open(os.path.join(save_path,'master_position.txt'),'a') as f:
#                     f.write(f"{timestamp},{master_position['lat']},{master_position['lon']}\n")
        
#         print('timestamp')
#         print(timestamp)
#         print('acoustic_position')
#         print(acoustic_position['x'],acoustic_position['y'],acoustic_position['z'])
#         print('global_position')
#         print(global_position['lat'],global_position['lon'])
#         print('master_position')
#         print(master_position['lat'],master_position['lon'])
#         print('')
    

# if __name__ == "__main__":
#     main()
