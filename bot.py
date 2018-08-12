import telebot
import config
import db
import state
import commands as com
import urllib


from users import User

bot = telebot.TeleBot(config.token)
users = {}

@bot.message_handler(commands=["start"])
def start(message):
    id = message.from_user.id
    check_if_user_in(id)
    if isAdmin(id):
        set_admin_start(id)
    else:
        set_start_screen(id)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_text(message):
    print("Message from id - {}, name - {} : {}".format(message.from_user.id, message.from_user.username, message.text))
    id = message.from_user.id
    check_if_user_in(id)
    handle_command(message.text, id)


@bot.message_handler(content_types=["photo"])
def handle_document(message):
    print("Got photos")
    id = message.from_user.id
    check_if_user_in(id)
    if isAdmin(id) and len(users[id].adminAdding) >= 5:
        idFile = 0
        photo = message.photo[len(message.photo)-1]
        idFile += 1
        file_info = bot.get_file(photo.file_id)
        file_path = file_info.file_path
        dir = "photo_{}_{}.jpg".format(users[id].adminAdding[0], len(users[id].adminAdding))
        users[id].adminAdding.append(dir)
        urllib.request.urlretrieve('https://api.telegram.org/file/bot' + config.token + '/' + file_path, "images/" + dir)
        pass


def check_if_user_in(id):
    if id not in users and isAdmin(id):
        users[id] = User(id, state.adminMain)
    if id not in users:
        users[id] = User(id, state.mainMenu)


def set_admin_start(id):
    users[id].state = state.adminMain
    users[id].admin_refresh()
    mark = create_markup([com.adminMenu, com.userMenu])
    bot.send_message(id, "Выберите тип меню", reply_markup=mark)


def set_admin_menu(id):
    users[id].state = state.adminMenu
    mark = create_markup([com.adminAddCar, com.adminDeleteCar, com.userBack])
    bot.send_message(id, "Выберите функцию", reply_markup=mark)


def set_admin_delete_cars(id):
    users[id].state = state.adminDeleting
    if len(users[id].adminDelete) > 0:
        msg = ""
        for car in users[id].adminDelete:
            msg += "#{} \n".format(car)
        bot.send_message(id,"Текущие объявления на удаление: \n{}".format(msg))
    list_cars(id, [com.adminAcceptDeleting, com.adminDeclineDeleting])
    bot.send_message(id, "Выберите номер объявления с машиной, которую хотите удалить.")

def set_admin_add_car(id):
    users[id].state = state.adminAdding
    users[id].adminAdding = []
    bot.send_message(id, "Введите название машины", reply_markup=telebot.types.ReplyKeyboardRemove())

def set_start_screen(id):
    if id not in users:
        users[id] = User(id, state.mainMenu)

    users[id].state = state.mainMenu
    coms_list = [com.carsList]
    if isAdmin(id):
        coms_list.append(com.userBack)
    mark = create_markup(coms_list)
    bot.send_message(id, "Бот автопродаж", reply_markup=mark)


def create_markup(row_list):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    for row in row_list:
        user_markup.row(row)
    return user_markup


def isAdmin(id):
    return id in config.admins

def handle_command(cmd, id):

    #users states

    if users[id].state == state.mainMenu:
        if cmd == com.carsList:
            list_cars(id, [com.userBack])
            users[id].state = state.listingCars
            return
        if cmd == com.userBack and isAdmin(id):
            set_admin_start(id)
            return

    if users[id].state == state.listingCars:
        if cmd == com.userBack:
            set_start_screen(id)
            return
        get_car(cmd, id)
        return

    if not isAdmin(id):
        bot.send_message(id, "Не понял, давай еще раз.")
        set_start_screen(id)
        return

    #admin states
    if users[id].state == state.adminMain:
        if cmd == com.userMenu:
            set_start_screen(id)
            return
        if cmd == com.adminMenu:
            set_admin_menu(id)
            return

    if users[id].state == state.adminMenu:
        if cmd == com.adminDeleteCar:
            set_admin_delete_cars(id)
            return
        if cmd == com.adminAddCar:
            set_admin_add_car(id)
            return
        if cmd == com.userBack:
            set_admin_start(id)
            return

    if users[id].state == state.adminAdding:
        if len(users[id].adminAdding) == 0:
            users[id].adminAdding.append(cmd)
            bot.send_message(id, "Введите описание")
            return
        if len(users[id].adminAdding) == 1:
            users[id].adminAdding.append(cmd)
            bot.send_message(id, "Введите модель")
            return
        if len(users[id].adminAdding) == 2:
            users[id].adminAdding.append(cmd)
            bot.send_message(id, "Введите пробег")
            return
        if len(users[id].adminAdding) == 3:
            users[id].adminAdding.append(cmd)
            bot.send_message(id, "Введите стоимость")
            return
        if len(users[id].adminAdding) == 4:
            users[id].adminAdding.append(cmd)
            mark = create_markup([com.adminAcceptAdding, com.adminDeclineAdding])
            bot.send_message(id, "Добавьте картинки. После этого, "
                                 "подтвердите или отмените добавление объявления", reply_markup=mark)
            return
        if len(users[id].adminAdding) >= 5:
            if cmd == com.adminAcceptAdding:
                if len(users[id].adminAdding) == 5:
                    bot.send_message(id, "Сначала добавьте картинки, или нажмите отмена.")
                    return
                bot.send_message(id, "Товар успешно добавлен")
                db.add_car(users[id].adminAdding)
                users[id].adminAdding = []
                set_admin_start(id)
                return
        if cmd == com.adminDeclineAdding:
            bot.send_message(id, "Отмена")
            users[id].adminAdding = []
            set_admin_start(id)
            return
        return

    #Deleting
    if users[id].state == state.adminDeleting:
        if cmd == com.adminAcceptDeleting:
            for carId in users[id].adminDelete:
                db.delete_car_id(carId)
            users[id].adminDelete = []
            bot.send_message(id, "Объявления успешно удалены.")
            set_admin_start(id)
            return
        if cmd == com.adminDeclineDeleting:
            users[id].adminDelete = []
            set_admin_start(id)
            return
        #add regexp
        try:
            cmd = cmd.split(" ")[0][1:]
            print(cmd)
            int(cmd)
            if int(cmd) not in users[id].adminDelete:
                users[id].adminDelete.append(int(cmd))
            set_admin_delete_cars(id)
        except:
            bot.send_message(id, "Неверный номер машины.")
        return

    #
    bot.send_message(id, "Не понял, давай еще раз.")
    if isAdmin(id):
        set_admin_start(id)
    else:
        set_start_screen(id)


def list_cars(id, additionalMarks = []):
    cars = db.get_cars()
    carNames = []
    for car in cars:
        carNames.append("#{} Название: {}".format(car[0],car[1]))
    if len(additionalMarks) > 0:
        carNames += additionalMarks
    mark = create_markup(carNames)
    bot.send_message(id, "Список машин: ", reply_markup=mark)


def get_car(cmd, id):
    #get id from message
    cmd = cmd.split(" ")[0][1:]
    car = db.get_car_by_id(cmd)
    if car is None:
        bot.send_message(id, "Неверное имя машины")
        set_start_screen(id)
        return
    msg = "Название: {}\n".format(car[1])
    msg += "Описание: {}\n".format(car[2])
    msg += "Модель: {}\n".format(car[3])
    msg += "Пробег: {}\n".format(car[4])
    msg += "Стоимость: {}\n".format(car[5])
    bot.send_message(id, msg)
    photos = car[7].split("|")
    for photo in photos:
        send_photo(id, photo)
    list_cars(id, [com.userBack])
    #set_start_screen(id)


def send_photo(id, photo):
    photo = open('images/{}'.format(photo), 'rb')
    bot.send_photo(id, photo)


if __name__ == '__main__':
    print("Bot started")
    bot.polling()