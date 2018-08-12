import config
import mysql.connector

#util

def connect():
    db = mysql.connector.connect(user=config.dbusername, password=config.dbpassword,
                                 host="127.0.0.1", database=config.dbname)
    return db

def exec(command):
    db = connect()
    cursor = db.cursor()
    cursor.execute(command)
    try:
        cmd = cursor.fetchall()
        if len(cmd) == 1:
            cmd = cmd[0]
        if len(cmd) == 0:
            raise Exception
    except:
        print("No data to fetch")
        cmd = None
    db.commit()
    cursor.close()
    db.close()
    return cmd

# commands


def add_car(data):
    photodata = data[5:]
    print(photodata)
    photodata = "|".join(photodata)
    print(photodata)
    exec("Insert into auto (name, description, model, mileage, price, images) values ('{}','{}','{}',{},{},'{}')".
         format(data[0], data[1], data[2], data[3], data[4], photodata))


def get_cars():
    cars = exec("SELECT * FROM auto;")
    if type(cars) == tuple:
        cars = [cars]
    return cars;


def get_car_by_id(id):
    car = exec("SELECT * FROM auto WHERE id = '{}'".format(id))
    return car


def delete_car_id(id):
    exec("DELETE FROM auto WHERE id = {}".format(id))


def delete_car_name(name):
    exec("DELETE FROM auto WHERE name = '{}'".format(name))



