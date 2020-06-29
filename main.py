from fast_neural_style.neural_style.neural_style import transfer
from style_transfer.model import run_style_transfer
from torch.cuda import empty_cache
from config import TOKEN
import numpy as np
from PIL import Image
from io import BytesIO


first_image_file = {}
info = {}

def cancel(context, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('Покеда. Для повтора тыкните -> /start',
							  reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END


def start(context, update):
	reply_keyboard = [	
						['хочу свой стиль'],
						['candy', 'mosaic', 'rain_princess', 'udnie'],
					 ]


	update.message.reply_text(
					'Привет!\nКакой стиль вы бы хотели перенести на свою картинку?',
					reply_markup=ReplyKeyboardMarkup(reply_keyboard, 
					resize_keyboard=True, 
					one_time_keyboard=True))
	
	return GET_INFO


def get_info(context, update):
	user = update.message.from_user
	chat_id = update.message.chat_id
	user_choose = update.message.text

	info[chat_id] = [update.message.text, None]
	logger.info("Style of %s: %s", user.first_name, update.message.text)
	
	if user_choose == 'Хочу свой стиль!':
		update.message.reply_text('Жду картинку, которую хотите стилизовать,\nи после - картинку стиля.',
							  reply_markup=ReplyKeyboardRemove())
		return USR_STYLE
	else:
		update.message.reply_text('Жду вашу картинку.',
							  reply_markup=ReplyKeyboardRemove())
		return PHOTO



def photo(bot, update):
	chat_id = update.message.chat_id
	update.message.reply_text('Принял! Скоро пришлю результат.')
	print("Got image from {}".format(chat_id))

	# получаем информацию о картинке
	image_info = update.message.photo[-1]
	image_file = bot.get_file(image_info)
	first_image_file[chat_id] = image_file

	content_image_stream = BytesIO()
	first_image_file[chat_id].download(out=content_image_stream)
	info[chat_id][1] = content_image_stream
	del first_image_file[chat_id]

	output = transfer(info[chat_id][1], info[chat_id][0])
	empty_cache()

	# теперь отправим назад фото
	output_stream = BytesIO()
	output.save(output_stream, format='PNG')
	output_stream.seek(0)
	update.message.reply_text('Держите')
	bot.send_photo(chat_id, photo=output_stream)
	update.message.reply_text('Ниче так вышло. Для повтора тыкните -> /start')
	
	return ConversationHandler.END

def usr_style(bot, update):
	
	chat_id = update.message.chat_id
	
	print("Got image from {}".format(chat_id))

    # получаем информацию о картинке
	image_info = update.message.photo[-1]
	image_file = bot.get_file(image_info)

	if chat_id in first_image_file:
        # первая картинка, которая к нам пришла станет content image, а вторая style image
		update.message.reply_text('Принял! Скоро пришлю результат.')
		content_image_stream = BytesIO()
		first_image_file[chat_id].download(out=content_image_stream)
		del first_image_file[chat_id]

		style_image_stream = BytesIO()
		image_file.download(out=style_image_stream)

		output = run_style_transfer(content_image_stream, style_image_stream)
		empty_cache()

		# теперь отправим назад фото
		output_stream = BytesIO()
		output.save(output_stream, format='PNG')
		output_stream.seek(0)
		update.message.reply_text('Держите')
		bot.send_photo(chat_id, photo=output_stream)
		print("Sent Photo to user")
		update.message.reply_text('Ниче так вышло, но немного странно, да? Для повтора тыкните -> /start')
		return ConversationHandler.END
	else:
		first_image_file[chat_id] = image_file
		update.message.reply_text('Принял! Теперь картинку стиля.')
	


if __name__ == '__main__':
	from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
	from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler, Filters)
	import logging

	logging.basicConfig(
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		level=logging.INFO)
	logger = logging.getLogger(__name__)
	GET_INFO, PHOTO, USR_STYLE = range(3)
	
	updater = Updater(token=TOKEN)

	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],

		states={
			GET_INFO: [MessageHandler(Filters.text, get_info)],

			PHOTO: [MessageHandler(Filters.photo, photo)],

			USR_STYLE: [MessageHandler(Filters.photo, usr_style)],
		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)
	updater.dispatcher.add_handler(conv_handler)

	updater.start_polling()
	updater.idle()