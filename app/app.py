import tkinter as tk
from tkinter import ttk, messagebox, END, BooleanVar
import psycopg2
from psycopg2 import Error


class App:

    def __init__(self):
        self.root = self.create_root()
        self.connection = None
        self.fields_info = {}
        self.root.mainloop()

    def __del__(self):
        self.close_connection()
        self.root.destroy()

    def create_root(self):
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
        self.database_entry = ttk.Entry(connect_frame)
        self.database_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.database_entry.insert(0, 'db')

        username_label = ttk.Label(connect_frame, text="Пользователь:")
        username_label.grid(column=0, row=1, padx=5, pady=5, sticky=tk.W)
        self.username_entry = ttk.Entry(connect_frame)
        self.username_entry.grid(column=1, row=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        password_label = ttk.Label(connect_frame, text="Пароль:")
        password_label.grid(column=0, row=2, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ttk.Entry(connect_frame, show="*")
        self.password_entry.grid(column=1, row=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        host_label = ttk.Label(connect_frame, text="Хост:")
        host_label.grid(column=0, row=3, padx=5, pady=5, sticky=tk.W)
        self.host_entry = ttk.Entry(connect_frame)
        self.host_entry.grid(column=1, row=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.host_entry.insert(0, 'localhost')

        port_label = ttk.Label(connect_frame, text="Порт:")
        port_label.grid(column=0, row=4, padx=5, pady=5, sticky=tk.W)
        self.port_entry = ttk.Entry(connect_frame)
        self.port_entry.grid(column=1, row=4, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.port_entry.insert(0, '5432')

        # Кнопки управления таблицами
        connect_button = ttk.Button(connect_frame, text="Подключиться", command=self.on_connect)
        connect_button.grid(column=1, row=5, padx=5, pady=5, sticky=(tk.W, tk.E))

        create_table_button = ttk.Button(connect_frame, text="Создать таблицу", command=self.on_create_table)
        create_table_button.grid(column=0, row=5, padx=5, pady=5, sticky=(tk.W, tk.E))

        delete_table_button = ttk.Button(connect_frame, text="Удалить таблицу", command=self.on_delete_table)
        delete_table_button.grid(column=0, row=6, padx=5, pady=5, sticky=(tk.W, tk.E))

        save_table_button = ttk.Button(connect_frame, text="Сохранить таблицу", command=self.on_create_table_commit)
        save_table_button.grid(column=0, row=7, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Фрейм для вывода списка таблиц
        table_list_frame = ttk.LabelFrame(main_frame, text="Таблицы")
        table_list_frame.grid(column=1, row=0, padx=10, pady=10, sticky=(tk.N, tk.S))

        self.table_listbox = tk.Listbox(table_list_frame, width=20, height=15)
        self.table_listbox.grid(column=0, row=0, padx=5, pady=5, sticky=(tk.N, tk.S))
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)

        # Фрейм для создания/редактирования таблиц
        table_info_frame = ttk.LabelFrame(main_frame, text="Информация о таблице")
        table_info_frame.grid(column=2, row=0, padx=10, pady=10, sticky=(tk.N, tk.S))

        table_label = ttk.Label(table_info_frame, text="Таблица:")
        table_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
        self.table_entry = ttk.Entry(table_info_frame)
        self.table_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        field_list_frame = ttk.LabelFrame(table_info_frame, text="Поля")
        field_list_frame.grid(column=0, row=2, columnspan=2, padx=5, pady=5)

        self.field_listbox = tk.Listbox(field_list_frame, width=10)
        self.field_listbox.grid(column=0, row=0, padx=5, pady=5)
        self.field_listbox.bind('<<ListboxSelect>>', self.on_field_select)


        field_label_frame = ttk.Frame(field_list_frame)
        field_label_frame.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        field_name_label = ttk.Label(field_label_frame, text="Название:")
        field_name_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
        self.field_name_entry = ttk.Entry(field_label_frame)
        self.field_name_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        field_type_label = ttk.Label(field_label_frame, text="Тип:")
        field_type_label.grid(column=0, row=1, padx=5, pady=5, sticky=tk.W)
        self.field_type_combo = ttk.Combobox(field_label_frame, state="readonly",
                                             values=['Integer', 'Double precision', 'Text', 'Timestamp'])

        self.field_type_combo.grid(column=1, row=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        pk_label = ttk.Label(field_label_frame, text="Первичный ключ:")
        pk_label.grid(column=0, row=2, padx=5, pady=5, sticky=tk.W)
        self.var_pk = BooleanVar()
        pk_checkbtn = ttk.Checkbutton(field_label_frame, variable=self.var_pk)
        pk_checkbtn.grid(column=1, row=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        clear_field_button = ttk.Button(field_label_frame, text="Создать поле", command=self.on_clear_field_info)
        clear_field_button.grid(column=0, row=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        save_table_button = ttk.Button(field_label_frame, text="Удалить поле", command=self.on_delete_field)
        save_table_button.grid(column=0, row=4, padx=5, pady=5, sticky=(tk.W, tk.E))

        save_field_button = ttk.Button(field_label_frame, text="Сохранить поле", command=self.on_create_field)
        save_field_button.grid(column=0, row=5, padx=5, pady=5, sticky=(tk.W, tk.E))

        return root


    @staticmethod
    def error_handler(func):
        def inside(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except (Exception, Error) as error:
                print(f"Error while {func.__name__}: {error}")
                messagebox.showerror(f"Error while {func.__name__}", f"{error}")

        return inside

    @error_handler
    def create_connection(self, db_name="db", db_user="", db_password="", db_host="", db_port=""):
        self.connection = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)

    def close_connection(self):
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            self.connection = None
            print("Connection closed")

    @error_handler
    def get_tables(self):
        cursor = self.connection.cursor()
        with cursor:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = cursor.fetchall()
            self.tables_names = [table[0] for table in tables]

    @error_handler
    def get_table_fields(self, table_name):
        cursor = self.connection.cursor()
        with cursor:
            cursor.execute(f"""select "column_name", "data_type", "column_default"
                           from information_schema.columns
                           where table_name='{table_name}'
                           order by table_schema, table_name""")

            self.fields_info = {r[0]: {'data_type': r[1], "pk": r[2] is not None} for r in list(cursor.fetchall())}

    @error_handler
    def show_table_info(self, table_name):
        #fields
        self.get_table_fields(table_name)
        self.field_listbox.delete(0, tk.END)

        for index, field in enumerate(self.fields_info.keys()):
            self.field_listbox.insert(tk.END, field)

        # cur table name
        self.table_entry.delete(0, tk.END)
        self.table_entry.insert(0, table_name)
        # cur field
        self.clear_field_info()

    @error_handler
    def create_table(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""SELECT EXISTS (
                                SELECT * FROM information_schema.tables
                                WHERE table_name = '{table_name}'
                                );""")
            if cursor.fetchall()[0][0]:
                self.edit_table(table_name)
                return

            create_command = f"CREATE TABLE {table_name} (\n"
            for field, params in self.fields_info.items():
                create_command += f"{field}"+ f"{'serial PRIMARY KEY' if params['pk'] else f'{params['data_type']}'}"+",\n"
            create_command = create_command[:-2] + ');'

            cursor.execute(create_command)
            self.connection.commit()
            # print(create_command)

    def edit_table(self, table_name):
        temp = [(field, params['pk']) for field, params in self.fields_info.items()]
        primary_key = next(filter(lambda x: x[1], temp))[0]

        columns = ' ,'.join(self.fields_info.keys())

        with self.connection.cursor() as cursor:
            cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN {primary_key} DROP DEFAULT")
            cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {table_name}_pkey")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}_temp")
            cursor.execute(f"CREATE TABLE {table_name}_temp AS SELECT * FROM {table_name}")
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"CREATE TABLE {table_name} ({primary_key} serial PRIMARY KEY)")

            for field, params in self.fields_info.items():
                if field != primary_key:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {field} {params['data_type']}")

            cursor.execute(f"INSERT INTO {table_name} SELECT {columns} FROM {table_name}_temp")
            cursor.execute(f"DROP TABLE {table_name}_temp")

            self.connection.commit()

    @error_handler
    def delete_table(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE {table_name}")
            self.connection.commit()

    @error_handler
    def show_tables(self):
        self.get_tables()
        self.table_listbox.delete(0, tk.END)
        for index, table in enumerate(self.tables_names):
            self.table_listbox.insert(tk.END, table)

    @error_handler
    def show_field_info(self, field):
        self.field_name_entry.delete(0, tk.END)
        self.field_name_entry.insert(0, field)
        self.field_type_combo.set(self.fields_info[field]['data_type'])
        self.var_pk.set(self.fields_info[field]['pk'])

    def clear_fields_list(self):
        # clear
        self.field_listbox.delete(0, tk.END)
        # cur table name
        self.table_entry.delete(0, tk.END)
        self.clear_field_info()

    def clear_field_info(self):
        # cur field
        self.field_name_entry.delete(0, tk.END)
        self.field_type_combo.set('')
        self.var_pk.set(False)

    # event handlers
    def on_connect(self):
        'create connection to db and show all tables'
        db_name = self.database_entry.get()
        db_user = self.username_entry.get()
        db_password = self.password_entry.get()
        db_host = self.host_entry.get()
        db_port = self.port_entry.get()

        self.close_connection()

        self.create_connection(db_name, db_user, db_password, db_host, db_port)
        self.show_tables()

    def on_table_select(self, *args):
        x = self.table_listbox.curselection()
        cur_table_name = self.table_listbox.get(x)
        self.show_table_info(cur_table_name)
        # todo catch empty click

    def on_field_select(self, *args):
        x = self.field_listbox.curselection()
        cur_field_name = self.field_listbox.get(x)
        self.show_field_info(cur_field_name)

    def on_create_field(self):
        field_name = self.field_name_entry.get()
        self.fields_info[f'{field_name}'] = {
                'data_type': self.field_type_combo.get(),
                'pk': self.var_pk.get()
            }

        self.field_listbox.insert(tk.END, field_name)
        self.on_clear_field_info()

    def on_create_table(self):
        # clear
        self.clear_fields_list()
        self.clear_field_info()
        self.fields_info = {}
        self.table_entry.insert(0, 'untitled_table')

    def on_create_table_commit(self):
        table_name = self.table_entry.get()
        self.create_table(table_name)
        self.show_tables()
        self.clear_fields_list()
        self.clear_field_info()

    def on_delete_table(self):
        table_name = self.table_listbox.get(self.table_listbox.curselection())
        self.delete_table(table_name)
        self.show_tables()

    def on_clear_field_info(self):
        self.clear_field_info()
        self.field_name_entry.insert(0, 'untitled_field')

    def on_delete_field(self):
        table_name = self.table_entry.get()
        field_name = self.field_name_entry.get()
        self.fields_info.pop(field_name)
        self.create_table(table_name)
        self.clear_field_info()
        # self.show_table_info(table_name)
