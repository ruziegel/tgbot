import logging

import sqlalchemy
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ConversationHandler, CommandHandler
from config import BOT_TOKEN
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean, ForeignKey, Time
from sqlalchemy import select
from datetime import datetime, time

engine = create_engine('sqlite:///orderDB.db')
conn = engine.connect()

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
              Column('group_ids', String(200), nullable=True),
              Column('notifications', Boolean()),
              Column('note_time', Time(), nullable=True))
groups = Table('groups', metadata,
               Column('id', Integer(), primary_key=True),
               Column('name', String(200)),
               Column('order_ids', String(200)))

metadata.create_all(engine)
print(engine)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

reply_keyboard = [['/start']]
regular_customers_keybord = ReplyKeyboardMarkup([['Лидия'], ['Добавить'], ['Пропустить']])  # Получать из бд
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def start(update, _):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    username = user.username  # пользователь с которым мы сейчас общаемся
    all_users = [i[1] for i in conn.execute(select(users)).fetchall()]  # все пользователи из бд
    print('Пользователи в бд', all_users)
    print('Текущий пользователь', username)
    if username in all_users:
        # это старый пользователь
        pass
    else:
        #  это новый пользователь
        ins = users.insert().values(
            name=username,
            group_ids=sqlalchemy.sql.null(),
            notifications=False,
            note_time=time(0, 0, 0)
        )
        res = conn.execute(ins)
        conn.commit()
        print('Результат добавления пользователя:', res)
        await update.message.reply_html(f'''Привет {user.mention_html()}!. Это бот для напоминания о заказах. При помощи
         него ты сможешь создавать заказы для твоей рабочей группы и каждый день в определенное время бот будет 
         напоминать тебе о них.\nТеперь давай придумаем название для твоей рабочей группы:''')

        return 'groupName'


async def groupName(update, _):
    ans = update.message.text
    print(ans)
    ins = users.insert().values(
        name='ans',
        order_ids=None
    )
    res = conn.execute(ins)
    conn.commit()
    await update.message.reply_html(f'''Отлично! Группа {ans} создана. Теперь напиши ник пользователя Telegram, и когда он в следующий раз напишет мне, он узнает что добавлен в эту группу.''')

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            'groupName': [MessageHandler(filters.TEXT, groupName)]
            'addUser':[]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
