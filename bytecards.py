import sqlite3 
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style

def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcard_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL                    
        )                 
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            set_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            definition TEXT NOT NULL,
            FOREIGN KEY (set_id) REFERENCES flashcard_sets(id)
        )              
    ''')

def add_set(conn, name):
    cursor = conn.cursor()

    cursor.execute('''
       INSERT INTO flashcard_sets (name)            
       VALUES (?)             
    ''', (name,))

    set_id = cursor.lastrowid
    conn.commit()

    return set_id

def add_card(conn, set_id, word, definition):
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO flashcards (set_id, word, definition)
        VALUES (?, ?, ?)
    ''', (set_id, word, definition))

    card_id = cursor.lastrowid
    conn.commit()

    return card_id

def get_sets(conn):
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name FROM flashcard_sets                          
    ''')

    rows = cursor.fetchall()
    sets = {row[1]: row[0] for row in rows}  # creating dictionary of sets

    return sets

def get_cards(conn, set_id):
    cursor = conn.cursor()

    cursor.execute('''
        SELECT word, definition FROM flashcards
        WHERE set_id = ?           
    ''', (set_id,))

    rows = cursor.fetchall()
    cards = [(row[0], row[1]) for row in rows]  # create list of cards

    return cards

def delete_set(conn, set_id):
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM flashcard_sets
        WHERE id = ?          
    ''', (set_id,))

    conn.commit()
    sets_combobox.set('')
    clear_flashcard_display()
    populate_sets_combobox()

    global current_cards, card_index
    current_cards = []
    card_index = 0

def populate_sets_combobox():
    sets_combobox['values'] = tuple(get_sets(conn).keys())

    
def create_set():
    set_name = set_name_var.get()
    if set_name:
        if set_name not in get_sets(conn):
            set_id = add_set(conn, set_name)
            populate_sets_combobox()
            set_name_var.set('')
            word_var.set('')
            definition_var.set('')

def add_word():
    set_name = set_name_var.get()
    word = word_var.get()
    definition = definition_var.get()

    if set_name and word and definition:
        if set_name not in get_sets(conn):
            set_id = add_set(conn, set_name)
        else:
            set_id = get_sets(conn)[set_name]

        add_card(conn, set_id, word, definition)

        word_var.set('')
        definition_var.set('')

        populate_sets_combobox()


def delete_selected_set():
    set_name = sets_combobox.get()

    if set_name:
        result = messagebox.askyesno(
            'Confirmation', f'Are you sure you want to delete the "{set_name}" set?'
        )

        if result == tk.YES:
            set_id = get_sets(conn)[set_name]
            delete_set(conn, set_id)
            populate_sets_combobox()
            clear_flashcard_display()

def select_set():
    global current_cards, card_index

    set_name = sets_combobox.get()

    if set_name:
        set_id = get_sets(conn)[set_name]
        cards = get_cards(conn, set_id)

        current_cards = cards
        card_index = 0

        if cards:
            display_flashcards(cards)
        else:
            word_label.config(text="No cards in this set.")
            definition_label.config(text='')
    else:
        current_cards = []
        card_index = 0
        clear_flashcard_display()

def display_flashcards(cards):
    global card_index, current_cards

    current_cards = cards
    card_index = 0

    if not cards:
        clear_flashcard_display()
    else:
        show_card()

def clear_flashcard_display():
    word_label.config(text='')
    definition_label.config(text='')

def show_card():
    global card_index, current_cards

    if current_cards:
        if 0 <= card_index < len(current_cards):
            word, _ = current_cards[card_index]
            word_label.config(text=word)
            definition_label.config(text='')
        else:
            clear_flashcard_display()
    else:
        clear_flashcard_display()

def flip_card():
    global card_index, current_cards

    if current_cards:
        _, definition = current_cards[card_index]
        definition_label.config(text=definition)

def next_card():
    global card_index, current_cards

    if current_cards:
        card_index = (card_index + 1) % len(current_cards)
        show_card()


def prev_card():
    global card_index, current_cards

    if current_cards:
        card_index = (card_index - 1) % len(current_cards)
        show_card()


if __name__ == '__main__':
    conn = sqlite3.connect('flashcards.db')
    create_tables(conn)

    # Create Gui Window
    root = tk.Tk()
    root.title('ByteCards')
    root.geometry('500x400')

    style = Style(theme='superhero')
    style.configure('TLabel', font=('TkDefaultFont', 16))
    style.configure('TButton', font=('TkDefaultFont', 16))

    set_name_var = tk.StringVar()
    word_var = tk.StringVar()
    definition_var = tk.StringVar()

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    create_set_frame = ttk.Frame(notebook)
    notebook.add(create_set_frame, text='Create Set')

    ttk.Label(create_set_frame, text='Set Name:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=set_name_var, width=30).pack(padx=5, pady=5)

    ttk.Label(create_set_frame, text='Word:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=word_var, width=30).pack(padx=5, pady=5)

    ttk.Label(create_set_frame, text='Definition:').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=definition_var, width=30).pack(padx=5, pady=5)

    ttk.Button(create_set_frame, text='Add Word', command=add_word).pack(padx=5, pady=10)

    ttk.Button(create_set_frame, text='Save Set', command=create_set).pack(padx=5, pady=10)

    select_set_frame = ttk.Frame(notebook)
    notebook.add(select_set_frame, text='Select Set')

    sets_combobox = ttk.Combobox(select_set_frame, state='readonly')
    sets_combobox.pack(padx=5, pady=40)

    ttk.Button(select_set_frame, text='Select Set', command=select_set).pack(padx=5, pady=5)

    ttk.Button(select_set_frame, text='Delete Set', command=delete_selected_set).pack(padx=5, pady=5)

    flashcards_frame = ttk.Frame(notebook)
    notebook.add(flashcards_frame, text='Learn Mode')

    card_index = 0
    current_tabs = []

    word_label = ttk.Label(flashcards_frame, text='', font=('TkDefaultFont', 24))
    word_label.pack(padx=5, pady=40)

    definition_label = ttk.Label(flashcards_frame, text='')
    definition_label.pack(padx=5, pady=5)

    ttk.Button(flashcards_frame, text='Flip', command=flip_card).pack(side='left', padx=5, pady=5)
    ttk.Button(flashcards_frame, text='Next', command=next_card).pack(side='right', padx=5, pady=5)
    ttk.Button(flashcards_frame, text='Previous', command=prev_card).pack(side='right', padx=5, pady=5)

    # Bind keyboard commands
    root.bind('<Right>', lambda event: next_card())
    root.bind('<Left>', lambda event: prev_card())
    root.bind('<space>', lambda event: flip_card())

    root.mainloop()
