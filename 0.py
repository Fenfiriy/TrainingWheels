from selenium import webdriver
import time
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# from bs4 import BeautifulSoup

url = 'https://10minutemail.com'
# driver = webdriver.Edge('C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
# soup = BeautifulSoup(driver.page_source, 'html.parser')
# print(soup.prettify())
client = discord.Client()
drivers = dict()

opts = webdriver.firefox.options.Options()
# opts.binary_location = r'C:\Users\steph\AppData\Local\Programs\Opera GX\launcher.exe'
opts.headless = True


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    user = message.author
    if user == client.user:
        return
    if message.content.startswith('$'):
        if message.content == '$create':
            driver = webdriver.Firefox(options=opts)

            drivers[user] = driver
            driver.get(url)
            time.sleep(5)
            temp_mail = driver.find_element_by_id('mail_address').get_attribute('value')
            await message.channel.send('Your temporary mail is : %s' % temp_mail)

        elif user in drivers:
            driver = drivers[user]
            msgs_count = int(driver.find_element_by_id('inbox_count_number').text)
            messages = driver.find_elements_by_class_name('mail_message')
            if message.content == '$check':
                preview = ''
                if msgs_count > 0:
                    preview = ':\n'
                    for i in range(len(messages)):
                        msg = messages[i]
                        preview = preview + '(' + str(i + 1) + \
                            '). From: ' + msg.find_element_by_class_name('small_sender').text + \
                            ' | Subject: ' + msg.find_element_by_class_name('small_subject').text + \
                            ' | Date: ' + msg.find_element_by_class_name('small_date').text + '\n'
                await message.channel.send('You have ' + str(msgs_count) + ' messages in mailbox' + preview)

            elif message.content.startswith('$read '):
                try:
                    msg_index = int(message.content[6:])
                except ValueError:
                    await message.channel.send('Unsupported index')
                else:
                    if msg_index > msgs_count or msg_index <= 0:
                        await message.channel.send('The message with that index does not exist, you only have ' +
                                                   str(msgs_count) + ' messages')
                    else:
                        msg = messages[msg_index - 1]
                        print(msg.find_element_by_class_name('message_bottom').is_displayed())
                        if not msg.find_element_by_class_name('message_bottom').is_displayed():
                            msg.click()
                        txt_to_print = msg.find_element_by_class_name('message_bottom').text
                        await message.channel.send(txt_to_print)

            elif message.content.startswith('$reply_to '):
                try:
                    msg_index = int(message.content.split()[1])
                except ValueError:
                    await message.channel.send('Unsupported index')
                else:
                    if msg_index > msgs_count or msg_index <= 0:
                        await message.channel.send('The message with that index does not exist')
                    else:
                        msg = messages[msg_index - 1]
                        if not msg.find_element_by_class_name('message_bottom').is_displayed():
                            await message.channel.send('Maybe you should read it first?')
                        else:
                            msg.find_element_by_class_name('reply_message_text').send_keys("".join(message.content.split()[2:]))
                            msg.find_element_by_class_name('reply_message_submit').click()


            elif message.content == '$end':
                driver.quit()
                del drivers[user]
                await message.channel.send('Your session ended')
        else:
            await message.channel.send('Your session does not exist')

client.run(TOKEN)
