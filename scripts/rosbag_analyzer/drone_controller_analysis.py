import numpy as np
import matplotlib.pyplot as plt
from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_types_from_msg 

from rosbag_types import SmarcRosbagTypestore

def plot(error: np.ndarray, title:str, subtitle:str):
    for i in range(error.shape[-1]):
        plt.plot(error[:,i], label=f"{i}-dir")
    plt.plot(np.linalg.norm(error, axis=-1), '-.', color='black', alpha= 0.7, linewidth = 0.75, label="Norm")
    plt.title(title + subtitle)
    plt.minorticks_on()
    plt.grid(which='both')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{title}{subtitle}.png",dpi=300)
    # plt.show()
    plt.close()
    
    
def main():
    smarc_types = SmarcRosbagTypestore()
    typestore = smarc_types.construct_custom_typestore()
    exp_dict = {
        "_lateral_decrease_kW" : '/home/tko/colcon_ws/src/smarc2/rosbag2_2025_01_30-11_01_23/',
        "_lateral_increase_kR" : '/home/tko/colcon_ws/src/smarc2/rosbag2_2025_01_30-10_56_13/',
        "_lateral_decrease_kR" : '/home/tko/colcon_ws/src/smarc2/rosbag2_2025_01_30-10_57_57/',
        "_lateral_nominal" : '/home/tko/colcon_ws/src/smarc2/rosbag2_2025_01_30-10_53_53/',
        "_vertical_nominal" : '/home/tko/colcon_ws/src/smarc2/rosbag2_2025_01_30-10_48_16/',
        "_lateral_decrease_kx" : '/home/tko/colcon_ws/src/smarc2/rosbag2_2025_01_30-11_27_18/',
    }
    states = {}
    states['pos'] = []
    states['vel'] = [] 
    states['orientation'] = []

    for exp_key, exp_val in exp_dict.items():
        # Create reader instance and open for reading.
        with Reader(exp_val) as reader:
            # Topic and msgtype information is available on .connections list.
            for reader_connection in reader.connections:
                print(reader_connection.topic, reader_connection.msgtype)

            # Iterate over messages.
            for connection, timestamp, rawdata in reader.messages():
                if connection.topic == '/drone_controller':
                    msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
                    states['pos'].append(msg.data[0:3])
                    states['vel'].append(msg.data[3:6])
                    states['orientation'].append(msg.data[6:])

            for key, val in states.items():
                val = np.array(val)
                plot(val, key, exp_key)
            





if __name__ == "__main__":
    main()
