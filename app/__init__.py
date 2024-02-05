import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
from psycopg2 import Error

from app.config import *

def error_handler(func):
    def inside(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except (Exception, Error) as error:
            print("Error", error)
            messagebox.showerror("Error: ", error)
    return inside

@error_handler
def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
    # print(connection)
    return connection


@error_handler
def close_connection(connection):
    if connection:
        connection.close()
        print("Connection closed")


@error_handler
def get_tables(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = cursor.fetchall()
    cursor.close()
    return [table[0] for table in tables]


@error_handler
def get_table_fields(connection, table_name):
    cursor = connection.cursor()
    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'")
    fields = cursor.fetchall()
    cursor.close()
    return [field[0] for field in fields]


@error_handler
def show_table_info(connection, table_name):
    fields = get_table_fields(connection, table_name)
    print(fields)


@error_handler
def create_table(connection, table_name, primary_key, fields):
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"CREATE TABLE {table_name} ({primary_key} PRIMARY KEY)")
    for field in fields:
        field_name, field_type = field
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {field_name} {field_type}")
    connection.commit()
    cursor.close()


@error_handler
def edit_table(connection, table_name, primary_key, fields):
    cursor = connection.cursor()
    cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN {primary_key} DROP DEFAULT")
    cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {table_name}_pkey")
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}_temp")
    cursor.execute(f"CREATE TABLE {table_name}_temp AS SELECT * FROM {table_name}")
    cursor.execute(f"DROP TABLE {table_name}")
    cursor.execute(f"CREATE TABLE {table_name} ({primary_key} PRIMARY KEY)")
    for field in fields:
        field_name, field_type = field
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {field_name} {field_type}")
    cursor.execute(f"INSERT INTO {table_name} SELECT * FROM {table_name}_temp")
    cursor.execute(f"DROP TABLE {table_name}_temp")
    connection.commit()
    cursor.close()


@error_handler
def delete_table(connection, table_name):
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE {table_name}")
    connection.commit()
    cursor.close()


def on_connect():
    global connection
    db_name = database_entry.get()
    db_user = username_entry.get()
    db_password = password_entry.get()
    db_host = host_entry.get()
    db_port = port_entry.get()

    connection = create_connection(db_name, db_user, db_password, db_host, db_port)
    tables = get_tables(connection)
    table_listbox.delete(0, tk.END)
    for table in tables:
        table_listbox.insert(tk.END, table)


def on_table_select(event):
    table_name = table_listbox.get(table_listbox.curselection())
    show_table_info(connection, table_name)


def on_create_table():
    table_name = table_entry.get()
    primary_key = primary_key_entry.get()
    fields = []
    for field in field_listbox.get(0, tk.END):
        fields.append(field.split(","))

    create_table(connection, table_name, primary_key, fields)
    tables = get_tables(connection)
    table_listbox.delete(0, tk.END)
    for table in tables:
        table_listbox.insert(tk.END, table)



def on_edit_table():
    table_name = table_listbox.get(table_listbox.curselection())
    primary_key = primary_key_entry.get()
    fields = []
    for field in field_listbox.get(0, tk.END):
        fields.append(field.split(","))

        edit_table(connection, table_name, primary_key, fields)
        tables = get_tables(connection)
        table_listbox.delete(0, tk.END)
        for table in tables:
            table_listbox.insert(tk.END, table)


def on_delete_table():
    table_name = table_listbox.get(table_listbox.curselection())

    delete_table(connection, table_name)
    tables = get_tables(connection)
    table_listbox.delete(0, tk.END)
    for table in tables:
        table_listbox.insert(tk.END, table)




root = tk.Tk()
root.title("Admin PostgreSQL")

# Основные фреймы
main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))



# Фрейм для ввода данных подключения
connect_frame = ttk.LabelFrame(main_frame, text="Подключение к БД")
connect_frame.grid(column=0, row=0, padx=10, pady=10, sticky=(tk.N, tk.S))

database_label = ttk.Label(connect_frame, text="База данных:")
database_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
database_entry = ttk.Entry(connect_frame)
database_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))
database_entry.insert(0, 'db')

username_label = ttk.Label(connect_frame, text="Пользователь:")
username_label.grid(column=0, row=1, padx=5, pady=5, sticky=tk.W)
username_entry = ttk.Entry(connect_frame)
username_entry.grid(column=1, row=1, padx=5, pady=5, sticky=(tk.W, tk.E))

password_label = ttk.Label(connect_frame, text="Пароль:")
password_label.grid(column=0, row=2, padx=5, pady=5, sticky=tk.W)
password_entry = ttk.Entry(connect_frame, show="*")
password_entry.grid(column=1, row=2, padx=5, pady=5, sticky=(tk.W, tk.E))

host_label = ttk.Label(connect_frame, text="Хост:")
host_label.grid(column=0, row=3, padx=5, pady=5, sticky=tk.W)
host_entry = ttk.Entry(connect_frame)
host_entry.grid(column=1, row=3, padx=5, pady=5, sticky=(tk.W, tk.E))
host_entry.insert(0, 'localhost')

port_label = ttk.Label(connect_frame, text="Порт:")
port_label.grid(column=0, row=4, padx=5, pady=5, sticky=tk.W)
port_entry = ttk.Entry(connect_frame)
port_entry.grid(column=1, row=4, padx=5, pady=5, sticky=(tk.W, tk.E))
port_entry.insert(0, '5432')

connect_button = ttk.Button(connect_frame, text="Подключиться", command=on_connect)
connect_button.grid(column=0, row=5, padx=5, pady=5, sticky=(tk.W, tk.E))


# Кнопки управления таблицами
create_table_button = ttk.Button(connect_frame, text="Создать таблицу", command=on_create_table)
create_table_button.grid(column=0, row=6, padx=5, pady=5, sticky=(tk.W, tk.E))

edit_table_button = ttk.Button(connect_frame, text="Редактировать таблицу", command=on_edit_table)
edit_table_button.grid(column=0, row=7, padx=5, pady=5, sticky=(tk.W, tk.E))

delete_table_button = ttk.Button(connect_frame, text="Удалить таблицу", command=on_delete_table)
delete_table_button.grid(column=0, row=8, padx=5, pady=5, sticky=(tk.W, tk.E))



# Фрейм для вывода списка таблиц
table_list_frame = ttk.LabelFrame(main_frame, text="Таблицы")
table_list_frame.grid(column=1, row=0, padx=10, pady=10, sticky=(tk.N, tk.S))

table_listbox = tk.Listbox(table_list_frame, width=20, height=15)
table_listbox.grid(column=0, row=0, padx=5, pady=5, sticky=(tk.N, tk.S))
table_listbox.bind('<<ListboxSelect>>', on_table_select)


# Фрейм для создания/редактирования таблиц
table_info_frame = ttk.LabelFrame(main_frame, text="Информация о таблице")
table_info_frame.grid(column=2, row=0, padx=10, pady=10, sticky=(tk.N, tk.S))

# todo add current table name
table_label = ttk.Label(table_info_frame, text="Таблица:")
table_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
table_entry = ttk.Entry(table_info_frame)
table_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))


field_list_frame = ttk.LabelFrame(table_info_frame, text="Поля")
field_list_frame.grid(column=0, row=2, columnspan=2, padx=5, pady=5)
field_listbox = tk.Listbox(field_list_frame, width=40)
field_listbox.grid(column=0, row=0, padx=5, pady=5)

field_label_frame = ttk.Frame(field_list_frame)
field_label_frame.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))
# todo get field name
field_name_label = ttk.Label(field_label_frame, text="Название:")
field_name_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
field_name_entry = ttk.Entry(field_label_frame)
field_name_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))
# todo get field type
field_type_label = ttk.Label(field_label_frame, text="Тип:")
field_type_label.grid(column=0, row=1, padx=5, pady=5, sticky=tk.W)
field_type_combo = ttk.Combobox(field_label_frame, state="readonly", values=["Целый", "Вещественный", "Текст", "Дата/Время"])
field_type_combo.grid(column=1, row=1, padx=5, pady=5, sticky=(tk.W, tk.E))
# selection = combo.get()
# todo get is_checked
pk_label = ttk.Label(field_label_frame, text="Первичный ключ:")
pk_label.grid(column=0, row=2, padx=5, pady=5, sticky=tk.W)
pk_checkbtn = ttk.Checkbutton(field_label_frame)
pk_checkbtn.grid(column=1, row=2, padx=5, pady=5, sticky=(tk.W, tk.E))
# todo check args
add_field_button = ttk.Button(field_label_frame, text="Добавить",
                              command=lambda: field_listbox.insert(tk.END, f"{field_name_entry.get()}, {field_type_combo.get()}, {pk_checkbtn.getint()}"))
add_field_button.grid(column=0, row=3, padx=5, pady=5, sticky=(tk.W, tk.E))



root.mainloop()
close_connection(connection)
