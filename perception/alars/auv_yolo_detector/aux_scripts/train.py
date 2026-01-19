from ultralytics import YOLO
# Load a COCO-pretrained YOLOv8n model
model = YOLO("best_sim.pt")

# Display model information (optional)
model.info()

# Train the model on the COCO8 example dataset for 100 epochs
results = model.train(data="config.yaml",
                      device = 'cpu', 
                      epochs= 10,
                      batch = 8,
                      imgsz = [640, 480],
                      
                      degrees = 180,
                      shear = -5,
                      hsv_h = 0.01, # Hue Adjustment

                      patience = 10
                      )
path = None #TODO: insert your path
model.save(path)

