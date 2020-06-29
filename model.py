from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as models
from scipy import misc


# В данном классе мы хотим полностью производить всю обработку картинок, которые поступают к нам из телеграма.
# Это всего лишь заготовка, поэтому не стесняйтесь менять имена функций, добавлять аргументы, свои классы и
# все такое.
class StyleTransferModel:
    def __init__(self):
        # Сюда необходимо перенести всю иницализацию, вроде загрузки свеерточной сети и т.д.
        pass

    def transfer_style(self, content_img_stream, style_img_stream):
        # Этот метод по переданным картинкам в каком-то формате (PIL картинка, BytesIO с картинкой
        # или numpy array на ваш выбор). В телеграм боте мы получаем поток байтов BytesIO,
        # а мы хотим спрятать в этот метод всю работу с картинками, поэтому лучше принимать тут эти самые потоки
        # и потом уже приводить их к PIL, а потом и к тензору, который уже можно отдать модели.
        # В первой итерации, когда вы переносите уже готовую модель из тетрадки с занятия сюда нужно просто
        # перенести функцию run_style_transfer (не забудьте вынести инициализацию, которая
        # проводится один раз в конструктор.

        # Сейчас этот метод просто возвращает не измененную content картинку
        # Для наглядности мы сначала переводим ее в тензор, а потом обратно
        return misc.toimage(self.process_image(content_img_stream)[0])

    # В run_style_transfer используется много внешних функций, их можно добавить как функции класса
    # Если понятно, что функция является служебной и снаружи использоваться не должна, то перед именем функции
    # принято ставить _ (выглядит это так: def _foo() )
    # Эта функция тоже не является
    def process_image(self, img_stream):
        # TODO размер картинки, device и трансформации не меняются в течении всей работы модели,
        # поэтому их нужно перенести в конструктор!
        imsize = 128
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(device)
        loader = transforms.Compose([
            transforms.Resize(imsize),  # нормируем размер изображения
            transforms.CenterCrop(imsize),
            transforms.ToTensor()])  # превращаем в удобный формат

        image = Image.open(img_stream)
        image = loader(image).unsqueeze(0)
        return image.to(device, torch.float)