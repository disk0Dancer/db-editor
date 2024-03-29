# Тестовое задание 
### Вакансия: Младший BI-Разработчк "Smart Analytics"
### Разработать десктопное приложение, которое представляет из себя редактор таблиц базы данных и выполняет следующие функции:
- При запуске формы открывается подключение к БД 
- Слева отображается список пользовательских таблиц, которые есть в БД 
- Справа пользователю предоставляется интерфейс для создания, удаления и редактирования таблиц в БД: 
  - При создании/редактировании таблицы есть возможность:
    - задать имя,
    - первичный ключ,
    - список полей. 
  - Пользователь может выбрать имя поля и один из следующих типов:
    - целочисленный,
    - вещественный,
    - текстовый,
    - даты/времени. 
- При возникновении ошибки приложение не прекращает работу и не закрывается.
- Сообщения об ошибках выводятся пользователю в диалоговом окне

- Предоставить как скомпилированное приложение, так и исходники.

### Стек технологий
- Python Tkinter
- СУБД: postgres


### Пример работы

<img width="1270" alt="image" src="https://github.com/gchurakov/db-editor/assets/89835485/4da2e7ee-0fa1-469f-9b6f-195a6bce47ed">


### Quick Start

1. Запустить проект
- `git clone git@github.com:gchurakov/db-editor.git`
- `cd db-editor`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements`
- `python3 run.py`

3. [Скачать приложение для Mac](https://github.com/gchurakov/db-editor/files/14222113/PostrgeSQL.GUI.Editor.app.zip)
4. [Скачать приложение для Windows](https://github.com/gchurakov/db-editor/files/14235475/PostgreSQL_GUI_Editor.exe.zip)

