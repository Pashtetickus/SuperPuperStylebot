import numpy as np
import torch
from torchvision import transforms
from PIL import Image
from .transformer_net import TransformerNet
from . import utils
import re

def transfer(content_img_stream, style):
    device = torch.device("cpu")

    content_image = Image.open(content_img_stream)
    content_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x.mul(255))
    ])
    content_image = content_transform(content_image)
    content_image = content_image.unsqueeze(0).to(device)

    with torch.no_grad():
        style_model = TransformerNet()
        path = 'fast_neural_style/saved_models/'+ style + '.pth'
        # state_dict = torch.load('fast_neural_style/saved_models/mosaic.pth')
        state_dict = torch.load(path)
        # remove saved deprecated running_* keys in InstanceNorm from the checkpoint
        for k in list(state_dict.keys()):
            if re.search(r'in\d+\.running_(mean|var)$', k):
                del state_dict[k]
        style_model.load_state_dict(state_dict)
        style_model.to(device).cpu()
        output = style_model(content_image)
        print(output.shape)

    return utils.save_image(output[0])
    ''' 
    utils.save_image(output[0])
    Почему не работает `import utils`,
    но работает абсолютный импорт 
    `from fast_neural_style.neural_style.utils import save_image`?

    '''
