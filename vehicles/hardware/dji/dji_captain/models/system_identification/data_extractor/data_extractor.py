import os
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

import yaml
import pandas as pd

def load_topics(yaml_filepath):
    
    with open(yaml_filepath, 'r') as file:
        config = yaml.safe_load(file)

    topic_dict = config['selected_topics']
    topic_class_map = {name: get_message(t) for name, t in topic_dict.items()}

    print(f"Successfully loaded {len(topic_class_map)} topics ready for extraction.")
    return topic_class_map


def flatten_message(msg, prefix=''):
    
    out = {}
    if hasattr(msg, 'get_fields_and_field_types'):
        for field in msg.get_fields_and_field_types():
            out.update(flatten_message(getattr(msg, field), f"{prefix}{field}_"))
            
    elif hasattr(msg, '__len__') and not isinstance(msg, (str, bytes)):   
        for i, item in enumerate(msg):
            out.update(flatten_message(item, f"{prefix}{i}_"))
            
    else:                                                    
        out[prefix.rstrip('_')] = msg
        
    return out


def extract_topic_data(bag_path, topic_class_map):
    
    reader = rosbag2_py.SequentialReader()
    storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id='sqlite3')
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr',
    )
    reader.open(storage_options, converter_options)

    reader.set_filter(rosbag2_py.StorageFilter(topics=list(topic_class_map.keys())))

    rows = {topic: [] for topic in topic_class_map.keys()}

    while reader.has_next():
        (topic, data, timestamp) = reader.read_next()
        if topic not in topic_class_map:
            continue

        msg = deserialize_message(data, topic_class_map[topic])

        record = {
            'bag_timestamp_sec': timestamp / 1e9,   
            'header_timestamp_sec': None,
        }
        if hasattr(msg, 'header'):
            stamp = msg.header.stamp
            record['header_timestamp_sec'] = stamp.sec + stamp.nanosec / 1e9

        record.update(flatten_message(msg))
        rows[topic].append(record)

    return {topic: pd.DataFrame(recs) for topic, recs in rows.items()}


def save_raw(dataframes, out_dir):
    
    os.makedirs(out_dir, exist_ok=True)
    for topic, df in dataframes.items():
        if df.empty:
            continue
        fname = topic.strip('/').replace('/', '__') + '.parquet'
        df.to_parquet(os.path.join(out_dir, fname), index=False)
    print(f"Saved {sum(not d.empty for d in dataframes.values())} topics to {out_dir}")


def print_summary(dataframes):
    
    print("\n--- EXTRACTION SUMMARY ---")
    for topic, df in dataframes.items():
        n = len(df)
        if n > 1:
            span = df['bag_timestamp_sec'].iloc[-1] - df['bag_timestamp_sec'].iloc[0]
            rate = (n - 1) / span if span > 0 else float('nan')
            print(f"  {n:>7} msgs  {rate:6.1f} Hz   {topic}")
        else:
            print(f"  {n:>7} msgs            -    {topic}")

    missing = [t for t, df in dataframes.items() if df.empty]
    if missing:
        print(f"\nWARNING: {len(missing)} requested topics were empty/missing in the bag:")
        for t in missing:
            print(f"  - {t}")
    else:
        print("\nSUCCESS: All requested topics were found in the bag!")


if __name__ == '__main__':
    bag_path = ''
    out_dir = ''

    print(f'Extracting from: {bag_path}')
    topic_map = load_topics('/vehicles/hardware/dji/dji_captain/models/system_identification/data_extractor/config.yaml')
    dataframes = extract_topic_data(bag_path, topic_map)

    save_raw(dataframes, out_dir)
    print_summary(dataframes)