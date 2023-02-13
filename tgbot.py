import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ConversationHandler, CommandHandler
from config import BOT_TOKEN
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime

engine = create_engine('sqlite:///orderDB.db')

engine.connect()

engine = create_engine('sqlite:///orderDB.db')
engine.connect()

metadata = MetaData()

customers = Table('customers', metadata,
                  Column('id', Integer(), primary_key=True),
                  Column('name', String(200), unique=True),
                  Column('phone', String(200)),
                  Column('orders_count', Integer(), default=0))
orders = Table('orders', metadata,
               Column('id', Integer(), primary_key=True),
               Column('customer', Integer(), ForeignKey(customers.c.id), nullable=False),
               Column('date', DateTime(), default=datetime.now),
               Column('deadline', DateTime()),
               Column('desс', String(200)),
               Column('cost', Integer()),
               Column('complete', Boolean(), default=False))
users = Table('users', metadata,
              Column('id', Integer(), primary_key=True),
              Column('name', String(200), unique=True),
              Column('groups', String(200)),
              Column('notifications', Boolean()),
              Column('note_time', DateTime()))
groups = Table('groups', metadata,
               Column('id', Integer(), primary_key=True),
               Column('orders', String(200)))

metadata.create_all(engine)
print(engine)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

reply_keyboard = [['/start']]
regular_customers_keybord = ReplyKeyboardMarkup([['Лидия'], ['Добавить'], ['Пропустить']])  # Получать из бд
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!",
        reply_markup=markup
    )


async def add_order_start(up, con):
    await up.message.reply_text('Кто заказал?', reply_markup=regular_customers_keybord)
    return


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))

    application.run_polling()


if __name__ == '__main__':
    main()
