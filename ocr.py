import numpy as np
import torch
import cv2

from vietocr.tool.translate import translate, translate_beam_search, resize
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import config as cf


class NewPredictor(Predictor):
    def predict(self, img, return_prob=False):
        # process input
        h, w = img.shape[:2]
        new_w, image_height = resize(w, h, self.config['dataset']['image_height'],
                                     self.config['dataset']['image_min_width'],
                                     self.config['dataset']['image_max_width'])
        img = cv2.resize(img, (new_w, image_height))

        img = img.transpose(2, 0, 1)
        img = img / 255

        img = img[np.newaxis, ...]
        img = torch.FloatTensor(img)

        img = img.to(self.config['device'])

        if self.config['predictor']['beamsearch']:
            sent = translate_beam_search(img, self.model)
            s = sent
            prob = None
        else:
            s, prob = translate(img, self.model)
            s = s[0].tolist()
            prob = prob[0]

        s = self.vocab.decode(s)

        if return_prob:
            return s, prob
        else:
            return s


def ocr(images):
    config = Cfg.load_config_from_name('vgg_transformer')
    config['vocab'] = cf.vocab
    config['weights'] = cf.weights
    config['cnn']['pretrained'] = False
    config['device'] = 'cuda:0'
    config['predictor']['beamsearch'] = False
    detector = NewPredictor(config)
    res = {}
    for k, v in images.items():
        img = v[1]
        pred = detector.predict(img)
        res[k] = pred
    return res
