
import telebot
import openai
from telebot import types, util
from decouple import config


openai.api_key = config("openai")
api = config("api")

bot = telebot.TeleBot(api)


def generate_response(question, state):
    # Use the conversation state to generate a more relevant response
    prompt = "Q: {qst}\nA:".format(qst=question)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop = ["You:"]

    )
    # Return the response and an updated conversation state
    return {
        "text": response.choices[0].text,
        "state": state
    }

@bot.message_handler(commands=['start'])
def send_welcome(message):
    add_bot_to_group_keyboard = telebot.types.InlineKeyboardMarkup()
    add_bot_to_group_button = telebot.types.InlineKeyboardButton(text="Add me to your chat!", url="https://t.me/DevRebot?startgroup=new")
    add_bot_to_group_keyboard.add(add_bot_to_group_button)
    bot.send_message(
        message.chat.id,
        f"مرحبًا {message.from_user.first_name} ! - أنا هنا لمساعدتك في الرد على اسئلتك بالذكاء الاصطناعي يمكنك سؤالي الان اي شئ يخطر في بالك. \n\n",
        parse_mode="Markdown",
        reply_markup=add_bot_to_group_keyboard
        # reply_markup=telebot.types.ForceReply()
    )
    notify_admin(message)

# Welcoom
text_messages={

    "welcomeNewMember" :
                u"حياك الله {name} منورنا ياحلو ",
}
@bot.chat_member_handler()
def handelUserUpdates(message:types.ChatMemberUpdated):
    newResponse = message.new_chat_member
    if newResponse.status == "member":
        bot.send_message(message.chat.id,text_messages["welcomeNewMember"].format(name=newResponse.user.first_name))

        # Send the add bot to group button
    # add_bot_to_group_keyboard = telebot.types.InlineKeyboardMarkup()
    # add_bot_to_group_button = telebot.types.InlineKeyboardButton(text="Add bot to group", url="https://t.me/DevRebot?startgroup=new")
    # add_bot_to_group_keyboard.add(add_bot_to_group_button)
    # bot.send_message(
    #     message.chat.id,
    #     "Click the button below to add the bot to a group",
    #     reply_markup=add_bot_to_group_keyboard
    # )

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "استخدم الأمر /ask و أدخل سؤالك لإجابتي عليه.",
        parse_mode="Markdown",
        reply_markup=telebot.types.ForceReply()
    )

def notify_admin(message):
    # You can change the value of `ADMIN_ID` to the actual ID of your admin
    ADMIN_ID = 362469503
    bot.send_message(ADMIN_ID, f"New user entered the bot: {message.from_user.first_name} {message.from_user.last_name}")

# Dictionary to store the conversation state of each user
conversation_state = {}

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id
    if user_id not in conversation_state:
        conversation_state[user_id] = {}


    current_state = conversation_state[user_id]
    response = generate_response(message.text, current_state)

    # Update the conversation state
    conversation_state[user_id] = response["state"]
    bot.send_message(message.chat.id, response["text"])

@bot.message_handler(commands=['add_to_group'])
def add_to_group(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_add = telebot.types.InlineKeyboardButton("Add bot to group", url="https://t.me/DevRebot?startgroup=new")
    keyboard.add(button_add)
    bot.send_message(message.chat.id, "Click the button to add me to a group:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    response = generate_response(message.text)
    bot.send_message(
        message.chat.id,
        response,
        parse_mode="Markdown",
        reply_markup=telebot.types.ForceReply()
    )

if __name__ == "__main__":
    print('Bot is running...')
    bot.infinity_polling(allowed_updates=util.update_types)
