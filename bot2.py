import logging
from aiogram import Bot, Dispatcher, executor, types
from aiocryptopay import AioCryptoPay, Networks
import config2 as config
import random
import string
import requests
import time

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

cryptopay = AioCryptoPay(config.CRYPTO_TOKEN, network=Networks.TEST_NET)


async def pay_money(amount, id):
    try:
        payme = await cryptopay.create_check(asset='USDT', amount=amount)
        keyboard = types.InlineKeyboardMarkup()
        prize = types.InlineKeyboardButton(text="🎁", url=payme.bot_check_url)
        keyboard.add(prize)
        await bot.send_message(id, f'<b>[💸] Выплата:\n</b>\n<blockquote><b>Сумма: {amount}$</b></blockquote>',
                               reply_markup=keyboard)
    except Exception as e:
        await bot.send_message(id,
                               f'<b>[⛔] Ошибка..., прасти браток денег в казне нет</b>\nНе удалось выплатить <b>{amount}</b>!\nНапишите гею @fightIor за выплатой')
        for admid in config.ADMIN_IDS:
            await bot.send_message(admid,
                                   f"<b>ДАЛБОЕБ ПОПОЛНИ КАЗНУ НАХУЙ!</b>\nБот не может создать выплату!\n\nЮзер: {id}\nСумма: {amount}\n\nЛог ошибки: <b>{e}</b>")


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("[👋] Привет!  Спасибо что выбрали нас💚!")


@dp.channel_post_handler(chat_id=config.PAY_ID)
async def handle_new_bet(message: types.Message):
    try:
        bet_usd = message.text.split("($")[1].split(").")[0]
        bet_usd = float(bet_usd.replace(',', ''))
        bet_coment = message.text.split("💬 ")[1]
        bet_comment = bet_coment.lower()
        player_name = message.text.split("отправил(а)")[0].strip()
        user = message.entities[0].user
        player_id = user.id
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text="Сделать ставку", url=config.pinned_link)
        keyboard.add(url_button)
        bet_design = config.bet.format(bet_usd=bet_usd, player_name=player_name, bet_comment=bet_comment)
        await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/new_bet.png", "rb"), caption=bet_design,
                             reply_markup=keyboard)
        if bet_comment.startswith("куб"):
            if bet_comment in config.ag_dice:
                await handle_dice(message, bet_usd, bet_comment, player_id)
            else:
                await bot.send_message(config.MAIN_ID,
                                       "<blockquote><b>💬 | Вы указали неверную игру!\n\n📌 | Для получения средств обратно, напишите ТС-у из описания канала.</b></blockquote>")
        else:
            await bot.send_message(config.MAIN_ID,
                                   "<blockquote><b>💬 | Вы указали неверную игру!\n\n📌 | Для получения средств обратно, напишите ТС-у из описания канала.</b></blockquote>")
    except IndexError:
        player_name = message.text.split("отправил(а)")[0].strip()
        await bot.send_message(config.MAIN_ID,
                               f"<b>[⛔] Ошибка!</b>\n\n<blockquote><b>Игрок {player_name} не указал комментарий!\nНапишите администратору @fightIor за возвратом (-20% от ставки)!</b></blockquote>")
    except AttributeError as e:
        player_name = message.text.split("отправил(а)")[0].strip()
        await bot.send_message(config.MAIN_ID,
                               f"<b>[⛔] Ошибка!</b>\n\n<blockquote><b>Не удалось распознать игрока {player_name}!\nНапишите администратору @fightIor за возвратом</b></blockquote>")
    except Exception:
        await bot.send_message(config.MAIN_ID, "<b>[⛔] Произошла неизвестная ошибка при обработке ставки!</b>")



async def handle_dice(message, bet_usd, bet_comment, player_id):
    dice_value = await bot.send_dice(chat_id=config.MAIN_ID)
    dice_value = dice_value.dice.value

    bet_type = bet_comment.split(" ")[1].lower()

    if bet_type == "меньше":
        if dice_value in [1, 2, 3]:
            win_amount = bet_usd * config.cef
            try:
                await pay_money(win_amount, player_id)
                await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/win.png", "rb"),
                                     caption=f"<b>🎉 Поздравляем, вы выиграли   {win_amount}$!</b>\n\n<blockquote><b>🚀 Ваш выигрыш успешно отправлен чеком боту http://t.me/bscasino_bot</b></blockquote>")
            except Exception as e:
                logging.error(f"Ошибка при выплате: {e}")
                await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/win.png", "rb"), caption=f"<blockquote><b>🎉 Поздравляем, вы выиграли {win_amount}, но вы не зарегистрированы в боте: http://t.me/bscasino_bot.</b></blockquote>")
        else:
            await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/lose.png", "rb"),
                                 caption="<blockquote><b>❌ | К сожалению, вы проиграли.</b></blockquote>")
    elif bet_type == "больше":
        if dice_value in [4, 5, 6]:
            win_amount = bet_usd * config.cef
            try:
                await pay_money(win_amount, player_id)
                await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/win.png", "rb"),
                                     caption=f"<b>🎉 Поздравляем, вы выиграли   {win_amount}$!</b>\n\n<blockquote><b>🚀 Ваш выигрыш успешно отправлен чеком боту http://t.me/bscasino_bot</b></blockquote>")
            except Exception as e:
                logging.error(f"Ошибка при выплате: {e}")
                await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/win.png", "rb"),
                                     caption=f"<blockquote><b>🎉 Поздравляем, вы выиграли {win_amount}, но вы не зарегистрированы в боте: http://t.me/bscasino_bot.</b></blockquote>")
        else:
            await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/lose.png", "rb"),
                                 caption="<blockquote><b>❌ | К сожалению, вы проиграли.</b></blockquote>")
    elif bet_type in ["чет", "четное", "чёт"]:
        if dice_value in [2, 4, 6]:
            win_amount = bet_usd * config.cef
            try:
                await pay_money(win_amount, player_id)
                await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/win.png", "rb"),
                                     caption=f"<b>🎉 Поздравляем, вы выиграли   {win_amount}$!</b>\n\n<blockquote><b>🚀 Ваш выигрыш успешно отправлен чеком боту http://t.me/bscasino_bot</b></blockquote>")
            except Exception as e:
                logging.error(f"Ошибка при выплате: {e}")
                await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/win.png", "rb"),
                                     caption=f"<blockquote><b>🎉 Поздравляем, вы выиграли {win_amount}, но вы не зарегистрированы в боте: http://t.me/bscasino_bot.</b></blockquote>")
        else:
            await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/lose.png", "rb"),
                                 caption="<blockquote><b>❌ | К сожалению, вы проиграли.</b></blockquote>")
    elif bet_type in ["нечет", "нечетное", "нечётное"]:
        if dice_value in [1, 3, 5]:
            win_amount = bet_usd * config.cef
            try:
                await pay_money(win_amount, player_id)
                await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/win.png", "rb"),
                                     caption=f"<b>🎉 Поздравляем, вы выиграли   {win_amount}$!</b>\n\n<blockquote><b>🚀 Ваш выигрыш успешно отправлен чеком боту http://t.me/bscasino_bot</b></blockquote>")
            except Exception as e:
                logging.error(f"Ошибка при выплате: {e}")
                await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/win.png", "rb"),
                                     caption=f"<blockquote><b>🎉 Поздравляем, вы выиграли {win_amount}, но вы не зарегистрированы в боте: http://t.me/bscasino_bot.</b></blockquote>")
        else:
            await bot.send_photo(chat_id=config.MAIN_ID, photo=open("img/lose.png", "rb"),
                                 caption="<blockquote><b>❌ | К сожалению, вы проиграли.</b></blockquote>")
    else:
        await bot.send_message(config.MAIN_ID,
                               "<blockquote><b>💬 | Вы указали неверную игру!\n\n📌 | Для получения средств обратно, напишите ТС-у из описания канала.</b></blockquote>")


@dp.message_handler(commands=['create_invoice'])
async def create_invoice(message: types.Message):
    try:
        amount = float(message.text.split()[1])
        invoice = await cryptopay.create_invoice(asset='USDT', amount=amount)
        await message.reply(f"Создан счет для пополнения казны:\n{invoice.bot_invoice_url}")
    except (IndexError, ValueError):
        await message.reply("Используйте команду в формате: /create_invoice <сумма>")


@dp.message_handler(commands=['del_checks'])
async def delete_all_invoices(message: types.Message):
    checks = await cryptopay.get_checks(status='active')
    if message.from_user.id in config.ADMIN_IDS:
        await message.reply(checks)
    else:
        await message.reply("<b>[⛔] Ошибка!</b>\n\n<blockquote>Вы не являетесь администратором!</blockquote>")
    
@dp.message_handler(commands=['delete_check'])
async def delete_check(message: types.Message):
    if message.from_user.id in config.ADMIN_IDS:
        check_id = message.text.split('/delete_check ')
        await cryptopay.delete_check(check_id[1])
        await message.answer('Чек удалены')
    else:
        await message.reply("<b>[⛔] Ошибка!</b>\n\n<blockquote>Вы не являетесь администратором!</blockquote>")

@dp.message_handler(commands=['balance'])
async def check_balance(message: types.Message):
    if message.from_user.id in config.ADMIN_IDS:
        balance = await cryptopay.get_balance()
        await message.answer(balance)
    else:
        message.reply("пошел нахуй малыш")
        

@dp.message_handler(commands=['pay_money'])
async def cmd_paymoney(message: types.Message):
    if message.from_user.id in config.ADMIN_IDS:
        amount = float(message.text.split(" ")[2])
        id = int(message.text.split(" ")[1])
        await pay_money(amount, id)
        await message.reply("Средства успешно переведены")
    else:
        await message.reply("<b>[⛔] Ошибка!</b>\n\n<blockquote>Вы не являетесь администратором!</blockquote>")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)