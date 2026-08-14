import os
import yaml
import pandas as pd
import numpy as np
import plotting
import data_processing
import matplotlib.pyplot as plt 

YAML_FILE_PATH = '/home/aleba/alars/validate_bag/config.yaml'
CLOCK = 'bag_timestamp_sec'

if __name__ == '__main__':
    with open(YAML_FILE_PATH, 'r') as file:
        config = yaml.safe_load(file)

    paths_dict = config['paths']
    drone_name = paths_dict['drone_name']
    props = config['prop_names'][drone_name]
    odom_attributes = config['odom_attributes']
    flu_attributes = config['flu_attributes']
    attitude_attributes = config['attitue_attributes']
    vl_gf_attributes = config['vl_gf_attributes']

    start_segmentation = config['segment_window']['i_start']
    end_segmentation = config['segment_window']['i_end']

    segments = [(961, 1564), (2546, 3114), (3861, 4320), (753, 961)]

    bag_dir = paths_dict['bag_dir']
    extracted_dir = os.path.join(bag_dir, 'extracted')
    segmented_dir = os.path.join(bag_dir, 'segmented')
    plot_dir = os.path.join(bag_dir, 'data_analysis')
    processed_bag_dir = os.path.join(bag_dir, 'processed')

    analyse_timestamp = False 
    segment_data = False 
    process_data = False 
    other = False

    user_input = input('\nWhich operation whould you like to do?\n'
    '1 - Analyse timestamps\n' \
    '2 - Segment Data\n' \
    '3 - Process Data\n').strip()

    if user_input == '1':
        analyse_timestamp = True
    elif user_input == '2':
        segment_data = True
    elif user_input == '3':
        process_data = True
    elif user_input == '4':
        other=True
    else:
        print(f'Invalide argument')
    
    if analyse_timestamp:
        df_odom = pd.read_parquet(
        os.path.join(extracted_dir, f'{drone_name}__smarc__odom.parquet'))

        odom_time = df_odom[CLOCK]

        odom_points = np.column_stack([df_odom[attribute] for attribute in odom_attributes[:3]])
        plotting.static_path(points=odom_points, t=odom_time)
        plotting.animate_path(points=odom_points, t=odom_time)

        df_odom = data_processing.relative_clock(df=df_odom, clock=CLOCK)

        df_prop_dict = {}
        for prop in props:
            df_prop = pd.read_parquet(os.path.join(extracted_dir, f'{drone_name}__sensor__props__{prop}.parquet'))
            df_prop = data_processing.relative_clock(df=df_prop, clock=CLOCK)
            df_prop_dict[prop] = df_prop
            
        df_attitude = pd.read_parquet(os.path.join(extracted_dir, f'{drone_name}__wrapper__psdk_ros2__attitude.parquet'))
        df_attitude = data_processing.relative_clock(df=df_attitude, clock=CLOCK)

        df_flu_flight_control =  pd.read_parquet(os.path.join(extracted_dir, f'{drone_name}__wrapper__psdk_ros2__flight_control_setpoint_FLUvelocity_yawrate.parquet'))
        df_flu_flight_control = data_processing.relative_clock(df=df_flu_flight_control, clock=CLOCK)

        print('Topic time_vector length:\n'\
            f'df_odom:{len(df_odom["relative_clock"])}, start:{df_odom["relative_clock"].iloc[0]}, end:{df_odom["relative_clock"].iloc[-1]}\n'\
            f'df_attitude:{len(df_attitude["relative_clock"])}, start:{df_attitude["relative_clock"].iloc[0]}, end:{df_attitude["relative_clock"].iloc[-1]}\n'\
            f'df_flu_flight_control:{len(df_flu_flight_control["relative_clock"])}, start{df_flu_flight_control["relative_clock"].iloc[0]}, end:{df_flu_flight_control["relative_clock"].iloc[-1]}\n')

        for prop in props:
            df_prop = df_prop_dict[prop]
            print(f'prop/{prop}:{len(df_prop["relative_clock"])}, start:{df_prop["relative_clock"].iloc[0]}, end:{df_prop["relative_clock"].iloc[-1]}')

        flu_data_array = []
        for attribute in flu_attributes:
            flu_data_array.append(df_flu_flight_control[attribute].to_numpy())
        #flu_data_array = np.asarray(flu_data_array)
        
        print('Plotting signals over time')
        plotting.plot_data(time=df_flu_flight_control[CLOCK].to_numpy(), data=flu_data_array,
                               title=f'flu_flight_control )', subtitles=flu_attributes,
                               hover_index=True)
        
        print('Showing relative timestamp plots')
        plotting.plot_relative_timestamp(df_flu_flight_control['relative_clock'], 'FLU_flight_control')
        plotting.plot_relative_timestamp(df_odom['relative_clock'], 'Odom')
        plotting.plot_relative_timestamp(df_attitude['relative_clock'], 'Attitude')
        for prop in props:
            plotting.plot_relative_timestamp(df_prop_dict[prop]['relative_clock'], f'prop/{prop}')
            plotting.plot_data(
                df_prop_dict[prop][CLOCK].to_numpy(),
                df_prop_dict[prop]['data'].to_numpy(),
                f'prop/{prop}',
                subtitles=[f'prop/{prop}']
            )
        
        print(f'Printing relative offset from FLU_velocity\n'\
              f'odom:{df_odom[CLOCK].iloc[0] - df_flu_flight_control[CLOCK].iloc[0]}\n'\
              f'attitude:{df_attitude[CLOCK].iloc[0] - df_flu_flight_control[CLOCK].iloc[0]}\n')
        for prop in props:
            print(f'prop/{prop}:{df_prop_dict[prop][CLOCK].iloc[0] - df_flu_flight_control[CLOCK].iloc[0]} ')



    if segment_data:
        if len(segments) == 0:
            print('Insert bounds for data segmentation')
        else:
            df_flu = pd.read_parquet(os.path.join(extracted_dir, f'{drone_name}__wrapper__psdk_ros2__flight_control_setpoint_FLUvelocity_yawrate.parquet'))
            df_odom = pd.read_parquet(os.path.join(extracted_dir, f'{drone_name}__smarc__odom.parquet'))
            df_vl_gf = pd.read_parquet(os.path.join(extracted_dir, f'{drone_name}__wrapper__psdk_ros2__velocity_ground_fused.parquet'))
            df_attitude = pd.read_parquet(os.path.join(extracted_dir, f'{drone_name}__wrapper__psdk_ros2__attitude.parquet'))

            for i, segment in enumerate(segments):
                start = segment[0]
                end = segment[1]
                df_flu_seg = df_flu.iloc[start:end].reset_index(drop=True)
                data_processing.report_segment(df=df_flu_seg, name='FLU', clock=CLOCK)

                ts = df_flu_seg[CLOCK].iloc[0]
                te = df_flu_seg[CLOCK].iloc[-1]

                time_flu = df_flu_seg[CLOCK]

                df_odom_segmented = data_processing.segment_by_time(df=df_odom, t_start=ts, t_end=te, clock=CLOCK)

                df_props_segmented = {}
                for prop in props:
                    df_prop = pd.read_parquet(os.path.join(extracted_dir, f'{drone_name}__sensor__props__{prop}.parquet'))
                    df_props_segmented[prop] = data_processing.segment_by_time(df=df_prop, t_start=ts, t_end=te, clock=CLOCK)
                
                df_vl_gf_segmented = data_processing.segment_by_time(df=df_vl_gf, t_start=ts, t_end=te, clock=CLOCK)

                df_attitude_segmented = data_processing.segment_by_time(df=df_attitude, t_start=ts, t_end=te, clock=CLOCK)
                
                print('Segment contents:')

                # Odom
                data_processing.report_segment(df=df_odom_segmented, name='odom', clock=CLOCK)
                odom_points = np.column_stack([df_odom_segmented[attribute] for attribute in odom_attributes[:3]])
                odom_time = df_odom_segmented[CLOCK]
                plotting.static_path(points=odom_points, t=odom_time)

                odom_data_segmented = []
                for attribute in odom_attributes:
                    odom_data_segmented.append(df_odom_segmented[attribute])

                plotting.plot_data(time=df_odom_segmented[CLOCK], data=odom_data_segmented,
                                   title='smarc/odom after segmentation', subtitles=odom_attributes,
                                   hover_index=True)

                # Velocity Ground Fused 
                data_processing.report_segment(df=df_vl_gf_segmented, name='Velocity_Ground_Fused', clock=CLOCK)
                vl_gf_data_segmented = []
                for attribute in vl_gf_attributes:
                    vl_gf_data_segmented.append(df_vl_gf_segmented[attribute])
                plotting.plot_data_with_gaps(time=df_vl_gf_segmented[CLOCK], data=vl_gf_data_segmented,
                                   title='Velocity_ground_fused after segmentation', subtitles=vl_gf_attributes)
                
                if len(time_flu) != len(df_vl_gf_segmented[CLOCK]):
                    print(f'Velocity_ground_fused time length is not equal to the input lenght, difference of {len(time_flu) - len(df_vl_gf_segmented[CLOCK])} messages')
                else:
                    plotting.plot_relative_timestamp(time=(time_flu-df_vl_gf_segmented[CLOCK]), title='Relative time FLU vs Velocity_ground_fused')

                # Attitude
                data_processing.report_segment(df=df_attitude_segmented, name='attitude', clock=CLOCK)

                # Props
                for prop in props:
                    data_processing.report_segment(df=df_props_segmented[prop], name=f'prop/{prop}', clock=CLOCK)
                    if len(time_flu) != len(df_props_segmented[prop][CLOCK]):
                        print(f'prop/{prop} time length is not equal to the input lenght, difference of {len(time_flu)-len(df_props_segmented[prop][CLOCK])} messages')
                    else:
                        plotting.plot_relative_timestamp(time=(time_flu-df_props_segmented[prop][CLOCK]), title=f'Relative time FLU vs prop/{prop}')
                
                os.makedirs(segmented_dir, exist_ok=True)
                print(f'Saving segmented data into:{segmented_dir}')
                df_odom_segmented.to_parquet(os.path.join(segmented_dir, f'{drone_name}__smarc__odom_{i}.parquet'))
                df_attitude_segmented.to_parquet(os.path.join(segmented_dir, f'{drone_name}__wrapper__psdk_ros2__attitude_{i}.parquet'))
                df_flu_seg.to_parquet(os.path.join(segmented_dir, f'{drone_name}__wrapper__psdk_ros2__flight_control_setpoint_FLUvelocity_yawrate_{i}.parquet'))
                df_vl_gf_segmented.to_parquet(os.path.join(segmented_dir, f'{drone_name}__wrapper__psdk_ros2__velocity_ground_fused_{i}.parquet'))
                for prop in props:
                    df_props_segmented[prop].to_parquet(os.path.join(segmented_dir, f'{drone_name}__sensor__props__{prop}_{i}.parquet'))
                
                input("Press Enter to continue...")
                print('\n\n\n')

    if process_data:
        grid_freq = config['grid_freq']
        base_name, ext = os.path.splitext(paths_dict['processed_bag_name'])

        for seg_idx, segment in enumerate(segments):
            print(f'\nProcessing segment {seg_idx}')

            # FLU_flight_control
            df_flu_data_segmented = pd.read_parquet(os.path.join(segmented_dir, f'{drone_name}__wrapper__psdk_ros2__flight_control_setpoint_FLUvelocity_yawrate_{seg_idx}.parquet'))
            flu_data_array = []

            for attribute in flu_attributes:
                flu_data_array.append(df_flu_data_segmented[attribute])
            flu_data_array = np.asarray(flu_data_array)

            flu_time = df_flu_data_segmented[CLOCK]
            

            plotting.plot_data(time=flu_time, data=flu_data_array,
                               title=f'flu_flight_control (segment {seg_idx})', subtitles=flu_attributes,
                               hover_index=True)

            df_attitude_segmented = pd.read_parquet(os.path.join(segmented_dir, f'{drone_name}__wrapper__psdk_ros2__attitude_{seg_idx}.parquet'))
            attitude_quat = np.column_stack([df_attitude_segmented[attribute] for attribute in attitude_attributes])

            df_vl_gf_segmented = pd.read_parquet(os.path.join(segmented_dir, f'{drone_name}__wrapper__psdk_ros2__velocity_ground_fused_{seg_idx}.parquet'))
            vl_gf_data_segmented = []
            for attribute in vl_gf_attributes:
                vl_gf_data_segmented.append(df_vl_gf_segmented[attribute])

            vl_gf_xyz_world = np.column_stack(vl_gf_data_segmented)
            vl_gf_xyz_flu = data_processing.world_to_flu(
                t_world=df_vl_gf_segmented[CLOCK], world_xyz=vl_gf_xyz_world,
                t_att=df_attitude_segmented[CLOCK], quat_xyzw=attitude_quat, yaw_only=True)

            plotting.plot_series_comparison(
                time1=df_vl_gf_segmented[CLOCK], data1=[vl_gf_xyz_flu[:, 0], vl_gf_xyz_flu[:, 1], vl_gf_xyz_flu[:, 2]],
                label1='Velocity_Ground_Fused (yaw-rotated to FLU)',
                time2=flu_time, data2=list(flu_data_array[:3]), label2='FLU axes_0-2',
                title=f'Velocity_Ground_Fused (FLU) vs FLU (segment {seg_idx})', subtitles=vl_gf_attributes)

            
            ts = flu_time.iloc[0]
            te = flu_time.iloc[-1]
            grid = np.arange(ts, te, 1.0 / grid_freq)

            df_flu_filled = pd.DataFrame({CLOCK: flu_time})
            for j, attribute in enumerate(flu_attributes):
                df_flu_filled[attribute] = flu_time[j]


            flu_on_grid, _ = data_processing.decimate_topic(
                grid=grid, t_p=flu_time.to_numpy(), segmented_df=df_flu_data_segmented, name_list=flu_attributes,
                grid_freq=grid_freq
            )
            

            df_vl_gf_flu = pd.DataFrame({CLOCK: df_vl_gf_segmented[CLOCK].to_numpy()})
            for j, attribute in enumerate(vl_gf_attributes):
                df_vl_gf_flu[attribute] = vl_gf_xyz_flu[:, j]
            vl_gf_flu_on_grid, _ = data_processing.decimate_topic(
                grid=grid, t_p=df_vl_gf_flu[CLOCK].to_numpy(), segmented_df=df_vl_gf_flu,
                name_list=vl_gf_attributes, grid_freq=grid_freq)

            
            prop_on_grid = {}
            for prop in props:
                df_prop_segmented = pd.read_parquet(os.path.join(segmented_dir, f'{drone_name}__sensor__props__{prop}_{seg_idx}.parquet'))
                prop_grid, _ = data_processing.decimate_topic(
                    grid=grid, t_p=df_prop_segmented[CLOCK].to_numpy(), segmented_df=df_prop_segmented,
                    name_list=['data'], grid_freq=grid_freq)
                prop_on_grid[prop] = prop_grid['data']

            sysid_df = pd.DataFrame({CLOCK: grid})
            for attribute in flu_attributes:
                sysid_df[f'FLU_{attribute}'] = flu_on_grid[attribute]
            for attribute in vl_gf_attributes:
                suffix = attribute.split('_')[-1]
                sysid_df[f'FLUvelocity_ground_fused_{suffix}'] = vl_gf_flu_on_grid[attribute]
            for prop in props:
                sysid_df[f'prop_{prop}'] = prop_on_grid[prop]

            os.makedirs(processed_bag_dir, exist_ok=True)
            out_path = os.path.join(processed_bag_dir, f'{base_name}_{seg_idx}{ext}')
            sysid_df.to_parquet(out_path)
            print(f'Saved sysid data: {sysid_df.shape[0]} rows x {sysid_df.shape[1]} cols -> {out_path}')

            input("Press Enter to continue...")
        