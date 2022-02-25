from datetime import datetime
import os
import sys
import random
import time
import threading
import telebot
from telebot import types

# Modulleri ayri klasorlerde tutabilmek icin asagidakiler yapildi. !!! DIKKAT Surum Degisirken Path degisecek !!!
sys.path.append('/home/runner/BilkentYemekBot/PdfDownloader')
sys.path.append('/home/runner/BilkentYemekBot/MenuToImage')
sys.path.append('/home/runner/BilkentYemekBot/ImageCropper')
sys.path.append('/home/runner/BilkentYemekBot/KeepAlive')


# Kendi modullerimi yukleyen komutlar
from pdfdownloader import pdfdownloader


from menutoimage import menutoimage
from imagecropper import imagecropper

from keep_alive import keep_alive 

API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)

        

@bot.message_handler(commands=['start'])   
def yemek(message):
    bot.send_message(message.chat.id, "Hoşgeldin {isim}. Sol alt taraftaki menüden seçimini yapabilirsin.".format(isim = message.chat.first_name))

@bot.message_handler(commands=['ymk'])   
def yemeker(message):
    bot.send_message(message.chat.id, str(message))

@bot.message_handler(commands=['yemek'])

# Meal chechker and sender
def yemekPhoto(message):

    from datetime import date
    currentDate = date.today()
    currentWeek = int(currentDate.isocalendar()[1])
    with open('Database/lastCheckedWeek.txt') as f:
        lastCheckedWeek = int(f.read())
    if currentWeek > lastCheckedWeek :
        pdfdownloader()
        menutoimage()
        imagecropper()
        lastCheckedWeek = currentWeek
        wk = open('Database/lastCheckedWeek.txt', 'w')
        wk.write('{text}'.format( text = lastCheckedWeek))
        wk.close()

    idTxt = open('Database/idStore.txt', 'r+')
    ides = idTxt.readline()
    idler = ides.split(',')

    if not ( str(message.chat.id) in idler):
        no = open("Database/idStore.txt", "a")
        no.write(",{n}".format( n = message.chat.id))
        no.close()  

    date = datetime.now()
    weekday = date.weekday()
    weekday += 1
    photo = open('ImageCropper/DailyMenus/day{day}.png'.format(day = weekday), 'rb')
    bot.send_photo(message.chat.id,photo)
    gunler = ["","Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    bot.send_message(message.chat.id,"{day} günü yemekleri".format(day = gunler[weekday]))  


    # Sticker sender
    # time.sleep(4)
    # resim = random.randint(0,4)
    # sti = open('Stickers/{resimNo}.webp'.format(resimNo = resim), 'rb')
    # bot.send_sticker(message.chat.id, sti)
    idTxt = open('Database/votedIDsWeek{week}Day{day}.txt'.format(week = currentWeek, day = weekday), "a")
    idTxt.write("")
    idTxt.close()
    idTxt = open('Database/votedIDsWeek{week}Day{day}.txt'.format(week = currentWeek, day = weekday), 'r+')
    ides = idTxt.readline()
    idler = ides.split(',')
    idTxt.close()

    if not ( str(message.chat.id) in idler):
        markupyn = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markupyn.add('Evet', 'Hayır')
        msg = bot.send_message(message.chat.id,'Yemeği değerlendirmeye ne dersin', reply_markup=markupyn)
        # msg = bot.reply_to(message, 'Yemeği değerlendirmeye ne dersin',reply_markup=markupyn)
        bot.register_next_step_handler(msg, process_voting_step)

def process_voting_step(message):
    cevap = message.text
    if (cevap == 'Evet'):
        try:
            chat_id = message.chat.id
            date = datetime.now()
            currentDate = date.today()
            currentWeek = int(currentDate.isocalendar()[1])
            weekday = date.weekday()
            weekday += 1
            idTxt = open('Database/votedIDsWeek{week}Day{day}.txt'.format(week = currentWeek, day = weekday), 'r+')
            ides = idTxt.readline()
            idler = ides.split(',')

            if not ( str(chat_id) in idler):
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add('1', '2','3','4','5')
                msg = bot.send_message(message.chat.id, "Bugünkü yemeği ne kadar seviyorsun? (1-5)", reply_markup=markup)
                bot.register_next_step_handler(msg, process_saving_step)
            else:
                bot.send_message(chat_id,"Bir yemeğe en fazla 1 defa oy verebilirsin :)")    
        except Exception as e:
            bot.reply_to(message, 'Bir hata olustu')
    else:
        oylar = ["Unutma, oy namustur","Oy veren, yemeği seçer","Bir oy, bir yemeği değiştirebilir","Vereceğin oy Bilkent'lilerin kaderini değiştirebilirdi.","Oyuna sahip çıkmayan, midesine sahip çıkamaz."]
        oyMetni = random.randint(0,4)
        bot.send_message(message.chat.id,oylar[oyMetni])
        

def process_saving_step(message):
    try:
        chat_id = message.chat.id
        vote = message.text
        date = datetime.now()
        currentDate = date.today()
        currentWeek = int(currentDate.isocalendar()[1])
        weekday = date.weekday()
        weekday += 1
        no = open('Database/votedIDsWeek{week}Day{day}.txt'.format(week = currentWeek, day = weekday), 'a+')
        no.write(",{n},={v}".format( n = chat_id,v = vote))
        no.close()
        sonCevap = ""
        if ( vote == "1"):
            sonCevap = "Bu puan biraz fazla mı düşük oldu sanki?"
        elif (vote == "2"):
            sonCevap = "Bu yemeği yiyecek kadar aç olduğundaki seni hayal edemiyorum dostum. Kodlarımı cloud'a yükledim ne olur ne olmaz. Müjde, bu yemeği Bilkent'te artık daha az göreceksin."
        
        elif (vote == "3"):
            sonCevap = "Bu yemek beni pek açmadı diyorsun. Umarım yarınki yemeği beğenirsin."
        elif (vote == "4"):
            sonCevap = "Yemeği güzel ama bence de bir lezzet patlaması değil. 5 puan verilmez."
        elif (vote == "5"):
            sonCevap = "Yemede yanında yat diyorsun yani. 5'e öyle bir bastın ki aman tanrım kodlarımın satırlarında hissettim.  Bu yemek ancak bir sanat eseri olabilir. Fakat sen ne içtiğine de dikkat etsen iyi olur. Benden sana bir bot tavsiyesi"
        else:
            sonCevap = "Sınır tanımıyorum diyorsun. Hadi yine iyisin! Bizden kaçmaz evlat. "

        bot.send_message(chat_id,"Tebrikler, puanının " + vote + " olarak kaydedildi")
        bot.send_message(chat_id, sonCevap)
        time.sleep(3)
        if ( vote == "1" ):
            bot.send_message(chat_id, "Şaka yaptım canım. Bu yemeğe 1 bile çok. Sen ağzının tadını biliyorsun.")
        sti = open('Stickers/{resimNo}.webp'.format(resimNo = 5), 'rb')
        bot.send_sticker(message.chat.id, sti)
    except Exception as e:
        bot.reply_to(message, 'Bir hata olustu')


@bot.message_handler(commands=['yemek2'])
def yemekYarinPhoto(message):
    chat_id = message.chat.id
    from datetime import date
    date = datetime.now()
    weekday = date.weekday()
    weekday += 2
    if ( weekday <= 7):
        photo = open('ImageCropper/DailyMenus/day{day}.png'.format(day = weekday), 'rb')
        bot.send_photo(chat_id,photo)
        gunler = ["","Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
        bot.send_message(chat_id,"Yarının yani {day} gününün yemekleri".format(day = gunler[weekday]))

        # Oy verme oncesi
        date = datetime.now()
        currentDate = date.today()
        currentWeek = int(currentDate.isocalendar()[1])
        weekday = date.weekday()
        weekday += 1
        idTxt = open('Database/votedIDsWeek{week}Day{day}.txt'.format(week = currentWeek, day = weekday), 'r+')
        ides = idTxt.readline()
        idler = ides.split(',')
        
        if not ( str(chat_id) in idler):
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('1', '2','3','4','5')
            msg = bot.send_message(chat_id, "Bugünkü yemeği ne kadar seviyorsun?", reply_markup=markup)
            bot.register_next_step_handler(msg, process_saving_step)
        # else:
            # bot.send_message(chat_id,"Bugünkü yemeğe zaten oy verdin. Bir yemeğe en fazla 1 defa oy verebilirsin :)") 
    else:
        bot.send_message(message.chat.id,"Yarının yemekleri henüz yayınlanmadı dostum. Biraz sonra tekrar deneyebilirsin.")



bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()




# Daily notifications
def hourChecker():
    while True:
        time.sleep(5)
        today = datetime.now()
        dayOfTheYear = int(today.strftime('%j'))
        with open('Database/sonGun.txt') as er:
            lastCheckedDay = int(er.read())
            er.close()

        if dayOfTheYear > lastCheckedDay:
            an = datetime.now()
            if (an.hour == 9):              
                wk = open('Database/sonGun.txt', 'r+')
                wk.truncate(0)
                wk.write('{text}'.format( text = dayOfTheYear))
                wk.close()
                function_to_run()

def function_to_run():
    txt = open('Database/idStore.txt', 'r+')
    contents = txt.readline()
    idler = contents.split(',')
    idler = list(dict.fromkeys(idler))
    txt.close()
    for id in idler:
        notification_sender(id)
        
def notification_sender(id):
    try:
        date = datetime.now()
        weekday = date.weekday()
        weekday += 1
        gunler = ["","Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
        photo = open('ImageCropper/DailyMenus/day{day}.png'.format(day = weekday), 'rb')
        bot.send_photo(id,photo)
        bot.send_message(id,"{day} gününün yemekleri.".format(day = gunler[weekday]))
        print("BASARILI")
    except:
        print("BASARISIZ")
        pass

# def notification_sender(id):
#     try:
#         date = datetime.now()
#         weekday = date.weekday()
#         weekday += 1
#         gunler = ["","Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
#         photo = open('ImageCropper/DailyMenus/eriste.png'.format(day = weekday), 'rb')
#         bot.send_photo(id,photo)
#         bot.send_message(id,"Kaşarlı Cevizli Erişte gününüz afiyet olsun. Kaşarınız yağlı, ceviziniz bol olsun.")
#         print(id + "ye gonderim BASARILI")
#     except:
#         print(id + "ye gonderim BASARISIZ")
#         pass

# 
# bot.send_message(id, "Yemek Hatırlatması")
# date = datetime.now()
# weekday = date.weekday()
# weekday += 1
# photo = open('ImageCropper/DailyMenus/day{day}.png'.format(day = weekday), 'rb')
# bot.send_photo(id,photo)
# bot.send_message(id,"{day} gününün yemekleri".format(day = gunler[weekday]))
    


if __name__ == "__main__":
    threading.Thread(target=hourChecker).start()
    keep_alive() ##

bot.infinity_polling()


# token = os.environ['API_KEY'] ##
# bot.run(token) ##

# https://www.codementor.io/@garethdwyer/building-a-discord-bot-with-python-and-repl-it-miblcwejz#keeping-our-bot-alive