import torch
from torchvision import transforms

import numpy as np
from PIL import Image
import cv2

from models import TruckNN
from config import device, best_ckpt_src, inf_img_src, inf_vid_src, inf_out_src, inf_out_img_src, inf_out_vid_src, net
from utils import get_logger
from visualize import vis_angle_on_img


def inference_image(model, logger, img=np.array(Image.open(inf_img_src)), record=True, log=True):
    
    orig_img = img.copy()
    img = torch.from_numpy(img).permute(2, 0, 1) # D, H, W

    if net == "TruckNN":
        size = (80, 240)
    elif net == "TruckInception":
        size = (299, 299)

    transform = transforms.Compose([
        transforms.Resize(size),
        transforms.Lambda(lambda x: (x / 127.5) - 1),
    ])

    img = transform(img)
    img = img[np.newaxis, :]
    # Inference: 
    y_pred = model(img)
    angle = round(y_pred.squeeze().item(), 3)

    if log:
        logger.info("(3) Angle: {0} rad".format(angle))

    # draw angle on image 
    img = vis_angle_on_img(orig_img, angle)

    # Record
    if record:
        f = open(inf_out_src, "a")
        f.write("{0}".format(angle))
        f.close()
        cv2.imwrite(inf_out_img_src, img)
        logger.info("(3) Inference Finished. Output image: {0}".format(inf_out_img_src))
    
    return img, angle

def inference_video(model, logger, record=True, log=True):

    # Load video and initiate video capturing
    video_source = cv2.VideoCapture(inf_vid_src)
    frame_width = int(video_source.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_source.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_num = int(video_source.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video_source.get(cv2.CAP_PROP_FPS))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_out = cv2.VideoWriter(inf_out_vid_src, fourcc, fps, (frame_width, frame_height))
    f = open(inf_out_src, "a")
    logger.info("(3) Video Loaded. Inferencing ... ")

    for _ in range(frame_num):
        ret, frame = video_source.read()
        frame_show = frame.copy()

        frame_show, angle = inference_image(model, logger, img=frame_show, record=False, log=log)

        if record:
            f.write("{0}".format(angle))
            video_out.write(frame_show)
        
        if cv2.waitKey(1) == 27:
            break

    f.close()
    video_source.release()
    video_out.release()
    if record:
        logger.info("(4) Inference Finished. Output video: {0}".format(inf_out_vid_src))

if __name__ == "__main__":
    # init model
    logger = get_logger()
    logger.info("(1) Initiating Inference ... ")
    model = TruckNN()
    model = model.to(device)

    # load model weights
    state = torch.load(best_ckpt_src, map_location=torch.device(device))['model_state_dict']
    for key in list(state.keys()):
        state[key.replace('module.', '')] = state.pop(key)
    model.load_state_dict(state, strict=True)
    model.eval()
    logger.info("(2) Model Loaded ... ")

    # inference
    # inference_image(model, logger)
    inference_video(model, logger)
    