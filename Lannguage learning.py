import sqlite3

conn = sqlite3.connect('language_learning.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS vocabulary (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
    language TEXT NOT NULL,
    word TEXT NOT NULL,
    translation TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    word_id INTEGER,
    correct_attempts INTEGER DEFAULT 0,
    incorrect_attempts INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (word_id) REFERENCES vocabulary(word_id)
)
''')

conn.commit()


def add_word(language, word, translation):
    cursor.execute('''
    INSERT INTO vocabulary (language, word, translation) 
    VALUES (?, ?, ?)
    ''', (language, word, translation))
    conn.commit()
    print(f"Word '{word}' with translation '{translation}' added to {language} vocabulary.")


def add_user(name):
    cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
    conn.commit()
    user_id = cursor.lastrowid
    print(f"User '{name}' added with user ID {user_id}.")
    return user_id


import random

def quiz_user(user_id, language):
    cursor.execute('''
    SELECT word_id, word, translation FROM vocabulary 
    WHERE language = ? ORDER BY RANDOM() LIMIT 5
    ''', (language,))
    words = cursor.fetchall()

    for word_id, word, translation in words:
        user_answer = input(f"What is the translation of '{word}'? ")
        if user_answer.lower() == translation.lower():
            print("Correct!")
            cursor.execute('''
            INSERT INTO progress (user_id, word_id, correct_attempts) 
            VALUES (?, ?, 1) 
            ON CONFLICT(user_id, word_id) DO UPDATE 
            SET correct_attempts = correct_attempts + 1
            ''', (user_id, word_id))
        else:
            print(f"Wrong! The correct answer is '{translation}'.")
            cursor.execute('''
            INSERT INTO progress (user_id, word_id, incorrect_attempts) 
            VALUES (?, ?, 1) 
            ON CONFLICT(user_id, word_id) DO UPDATE 
            SET incorrect_attempts = incorrect_attempts + 1
            ''', (user_id, word_id))
        conn.commit()



def view_progress(user_id):
    cursor.execute('''
    SELECT v.word, v.translation, p.correct_attempts, p.incorrect_attempts
    FROM progress p
    JOIN vocabulary v ON p.word_id = v.word_id
    WHERE p.user_id = ?
    ''', (user_id,))
    progress = cursor.fetchall()
    
    for word, translation, correct, incorrect in progress:
        print(f"Word: {word}, Translation: {translation}, Correct Attempts: {correct}, Incorrect Attempts: {incorrect}")


def main():
    print("Welcome to the Language Learning App!")
    print("1. Register")
    print("2. Add Word")
    print("3. Quiz")
    print("4. View Progress")
    print("5. Exit")

    choice = input("Choose an option: ")
    
    if choice == '1':
        name = input("Enter your name: ")
        add_user(name)

    elif choice == '2':
        language = input("Enter the language: ")
        word = input("Enter the word: ")
        translation = input("Enter the translation: ")
        add_word(language, word, translation)

    elif choice == '3':
        user_id = int(input("Enter your user ID: "))
        language = input("Enter the language: ")
        quiz_user(user_id, language)

    elif choice == '4':
        user_id = int(input("Enter your user ID: "))
        view_progress(user_id)

    elif choice == '5':
        print("Goodbye!")
        conn.close()
        exit()
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    while True:
        main()