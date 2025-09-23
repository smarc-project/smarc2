import os

# Folder paths
combined_folder = "for_cnn_training_combined_from_dema"
points_folder = "for_cnn_training_points_from_dema"

# Get all P1_*.txt timestamps from points folder
points_timestamps = set()
for filename in os.listdir(points_folder):
    if filename.startswith("P1_") and filename.endswith(".txt"):
        timestamp = filename[3:-4]  # remove "P1_" and ".txt"
        points_timestamps.add(timestamp)

# Check each image in combined folder
for filename in os.listdir(combined_folder):
    if filename.startswith("combined_") and filename.endswith(".jpg"):
        timestamp = filename[9:-4]  # remove "combined_" and ".jpg"
        if timestamp not in points_timestamps:
            file_path = os.path.join(combined_folder, filename)
            print(f"Deleting: {file_path}")
            os.remove(file_path)
