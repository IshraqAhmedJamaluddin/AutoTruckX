import numpy as np
from PIL import Image

from config import best_ckpt_src, inf_img_src, net
from utils import select_model, load_weights, preprocess_img


def inference_image(model, img):
    img = preprocess_img(img, net)

    # Inference: 
    y_pred = model(img)
    angle = round(y_pred.squeeze().item(), 3)

    return angle

logger, model = select_model(model_name=net, init_msg=None)

# load model weights
load_weights(model, best_ckpt_src, logger)

print('Angle:', inference_image(model, np.array(Image.open(inf_img_src))))

