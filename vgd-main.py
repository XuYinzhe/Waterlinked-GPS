import os
import argparse
import json
import requests
import datetime
from pprint import pprint

def get_data(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as exc:
        print("Exception occured {}".format(exc))
        return None

    if r.status_code != requests.codes.ok:
        print("Got error {}: {}".format(r.status_code, r.text))
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

def get_imu_calibrate(base_url):
    return get_data("{}/api/v1/imu/calibrate".format(base_url))

def get_external_imu(base_url):
    return get_data("{}/api/v1/external/imu".format(base_url))

def get_external_orientation(base_url):
    return get_data("{}/api/v1/external/orientation".format(base_url))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-u",
        "--url",
        help = "Base URL to use",
        type = str,
        default = "https://demo.waterlinked.com")
    parser.add_argument(
        "-s",
        "--save",
        help = "Save dir",
        type = str,
        default = "save")
    parser.add_argument(
        "-n",
        "--notsave",
        help = "Don't save the recording",
        action = "store_true",)
    args = parser.parse_args()

    save_path = os.path.join(args.save,datetime.datetime.now().strftime("%m%d%H%M"))
    os.makedirs(save_path, exist_ok=True)

    base_url = args.url
    print("Using base_url: %s" % args.url)
    
    antenna_position = get_antenna_position(base_url)
    
    if not args.notsave:
        with open(os.path.join(save_path,'antenna_position.txt'),'w') as f:
            f.write(antenna_position.__str__())
        with open(os.path.join(save_path,'acoustic_position.txt'),'w') as f:
            f.write('t,x,y,z\n')
        with open(os.path.join(save_path,'global_position.txt'),'w') as f:
            f.write('t,lat,lon\n')
        with open(os.path.join(save_path,'master_position.txt'),'w') as f:
            f.write('t,lat,lon\n')

    while True:
        timestamp = datetime.datetime.now().strftime("%Y%m%d.%H%M%S%f")
        acoustic_position = get_acoustic_position(base_url)
        global_position = get_global_position(base_url)
        master_position = get_master_position(base_url)
        
        if not args.notsave:
            with open(os.path.join(save_path,'acoustic_position.txt'),'a') as f:
                f.write(f"{timestamp},{acoustic_position['x']},{acoustic_position['y']},{acoustic_position['z']}\n")
            with open(os.path.join(save_path,'global_position.txt'),'a') as f:
                f.write(f"{timestamp},{global_position['lat']},{global_position['lon']}\n")
            with open(os.path.join(save_path,'master_position.txt'),'a') as f:
                f.write(f"{timestamp},{master_position['lat']},{master_position['lon']}\n")
        
        print('timestamp')
        print(timestamp)
        print('acoustic_position')
        print(acoustic_position['x'],acoustic_position['y'],acoustic_position['z'])
        print('global_position')
        print(global_position['lat'],global_position['lon'])
        print('master_position')
        print(master_position['lat'],master_position['lon'])
        print('')
    

if __name__ == "__main__":
    main()
