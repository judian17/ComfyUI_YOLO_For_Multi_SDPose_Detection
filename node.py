import os
import cv2
import folder_paths
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("BBox Nodes: ultralytics library not found. YOLO detection will be disabled.")

# --- 初始化 YOLO 模型文件夹 ---
YOLO_MODEL_DIR = os.path.join(folder_paths.models_dir, "yolo")
folder_paths.add_model_folder_path("yolo", YOLO_MODEL_DIR, is_default=False)
os.makedirs(YOLO_MODEL_DIR, exist_ok=True)

class YOLOModelLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model_name": (folder_paths.get_filename_list("yolo"),)}}
    
    RETURN_TYPES = ("YOLO_MODEL",)
    FUNCTION = "load_yolo"
    CATEGORY = "SDPose/Utils"

    def load_yolo(self, model_name):
        if not YOLO_AVAILABLE:
            raise ImportError("ultralytics is not installed. Please pip install ultralytics.")
        model_path = folder_paths.get_full_path("yolo", model_name)
        return (YOLO(model_path),)

class BBoxYOLO:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "yolo_model": ("YOLO_MODEL",),
                "images": ("IMAGE",),
                "confidence_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
            }
        }
    
    # 严格匹配官方 io.BoundingBox.Input() 创建的底层数据类型
    RETURN_TYPES = ("BOUNDING_BOX",)
    FUNCTION = "detect"
    CATEGORY = "SDPose/Utils"

    def detect(self, yolo_model, images, confidence_threshold):
        all_bboxes = []
        images_np = images.cpu().numpy()
        
        for frame_idx in range(images.shape[0]):
            img_rgb = (images_np[frame_idx] * 255).astype(np.uint8)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            frame_bboxes = []
            
            # 运行 YOLO 推理
            results = yolo_model(img_bgr, verbose=False)
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        # 类别 0 在多数 YOLO 模型中代表 "person" (人)
                        if int(box.cls[0]) == 0 and float(box.conf[0]) > confidence_threshold: 
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
                            if x2 > x1 and y2 > y1:
                                frame_bboxes.append({
                                    "x": int(max(0, x1)), 
                                    "y": int(max(0, y1)),
                                    "width": int(x2 - x1), 
                                    "height": int(y2 - y1)
                                })
            
            # 将这一帧里的所有人框添加进总列表 (支持批处理多帧)
            all_bboxes.append(frame_bboxes)
            
        return (all_bboxes,)

# --- 注册节点 ---
NODE_CLASS_MAPPINGS = {
    "YOLOModelLoader": YOLOModelLoader,
    "BBoxYOLO": BBoxYOLO
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YOLOModelLoader": "Load YOLO Model (For SDPose)",
    "BBoxYOLO": "YOLO BBox Extractor"
}