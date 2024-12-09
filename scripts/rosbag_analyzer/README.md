# Ros Bag Analyzer

## Why:
You did some cool experiments, collected a ros bag and want to create fancy
plots. Or you want to do post-processing with the latest cutting edge filtering
algorithm. Either way, you want to get the data out of the ros bag.

## Prerequesits
[Rosbags package](https://ternaris.gitlab.io/rosbags/index.html), install with
```shell
pip install rosbags
```

## Usage
TL;DR: Change the file path to the **directory** with the ros bag, choose the
topics you want, save the data, here I used dictionaries with lists.

### Longer version
We have custom message types that we need to register with the package.
A generic solution has been implemented for smarc in the `rosbag_types.py` that imports all
the custom types in `smarc2/messages/` to be a convenient solution for all. See the example in the script
or in the documentation of the class.

The ros bag contains the `/parameter_events` topic, which records when a
ROS 2 parameter gets changed. I use this to change the trajectory and wanted to
visualize it here.
