import os
import glob
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image

# ===== 1. CNN Model Definition =====
class AnchorPointCNN(nn.Module):
    def __init__(self):
        super(AnchorPointCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)

        self.fc1 = nn.Linear(64 * 28 * 28, 256)  # If input is resized to 224x224
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 4)  # x1, y1, x2, y2

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # -> 112x112
        x = self.pool(F.relu(self.conv2(x)))  # -> 56x56
        x = self.pool(F.relu(self.conv3(x)))  # -> 28x28
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

# ===== 2. Custom Dataset Loader =====
class AnchorPointDataset(Dataset):
    def __init__(self, image_folder, annotations, output_size=(224, 224)):
        self.image_folder = image_folder
        self.annotations = annotations  # list of (filename, [x1, y1, x2, y2])
        self.output_size = output_size
        self.transform = transforms.Compose([
            transforms.Resize(output_size),
            transforms.ToTensor()
        ])
        self.original_size = (640, 480)  # width, height

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        filename, coords = self.annotations[idx]
        img_path = os.path.join(self.image_folder, filename)
        image = Image.open(img_path).convert("RGB")
        image = self.transform(image)

        x_scale = self.output_size[0] / self.original_size[0]
        y_scale = self.output_size[1] / self.original_size[1]
        x1, y1, x2, y2 = coords
        target = torch.tensor([x1 * x_scale, y1 * y_scale, x2 * x_scale, y2 * y_scale], dtype=torch.float32)

        return image, target

# ===== 3. Function to load annotations =====
def load_annotations(image_folder, annotation_folder):
    image_files = glob.glob(os.path.join(image_folder, "combined_*.jpg"))
    annotations = []

    for img_path in image_files:
        img_filename = os.path.basename(img_path)
        # extract timestamp part
        base_id = img_filename.replace("combined_", "").replace(".jpg", "")

        # corresponding annotation files
        p1_file = os.path.join(annotation_folder, f"P1_{base_id}.txt")
        p2_file = os.path.join(annotation_folder, f"P2_{base_id}.txt")

        if not os.path.isfile(p1_file) or not os.path.isfile(p2_file):
            print(f"Warning: Missing annotation for {img_filename}, skipping.")
            continue

        # Read coordinates
        with open(p1_file, 'r') as f1:
            x1, y1 = map(float, f1.read().strip().split())
        with open(p2_file, 'r') as f2:
            x2, y2 = map(float, f2.read().strip().split())

        # Add to annotation list
        annotations.append((img_filename, [x1, y1, x2, y2]))

    print(f"Total loaded samples: {len(annotations)}")
    return annotations

# ===== 4. Training Script =====
def main():
    # Paths
    image_folder = "for_cnn_training_combined_from_dema"
    annotation_folder = "for_cnn_training_points_from_dema"

    # Load real annotations
    annotations = load_annotations(image_folder, annotation_folder)

    # Dataset & Dataloader
    dataset = AnchorPointDataset(image_folder, annotations)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    # Model, loss, optimizer
    model = AnchorPointCNN()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    for epoch in range(100):
        running_loss = 0.0
        for images, targets in dataloader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        print(f"Epoch {epoch+1} | Loss: {running_loss / len(dataloader):.4f}")

    # Save model
    torch.save(model.state_dict(), "anchor_point_cnn.pth")
    print("Model saved to anchor_point_cnn.pth")

if __name__ == "__main__":
    main()
