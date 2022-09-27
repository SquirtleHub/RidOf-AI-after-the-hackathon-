from imageai.Detection import ObjectDetection

def init_detector(path):
    obj_detect = ObjectDetection()
    obj_detect.setModelTypeAsYOLOv3()
    obj_detect.setModelPath(path)
    obj_detect.loadModel()
    return obj_detect