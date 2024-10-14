import openai
from colorama import init, Fore, Style
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


def create_database():
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interactions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 question TEXT NOT NULL, 
                 answer TEXT NOT NULL, 
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
def get_all_interactions():
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    c.execute("SELECT * FROM interactions")
    interactions = c.fetchall()
    conn.close()
    return interactions

def add_interaction(question, answer):
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    c.execute("INSERT INTO interactions (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

def view_interactions():
    interactions = get_all_interactions()

    if len(interactions) == 0:
        print(Fore.RED + "No interactions found." + Style.RESET_ALL)
    else:
        print(Fore.MAGENTA + "\nQuestion-Answer Interactions:" + Style.RESET_ALL)
        print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)
        for interaction in interactions:
            print(f"ID: {interaction[0]}")
            print(f"Question: {interaction[1]}")
            print(f"Answer: {interaction[2]}")
            print(f"Timestamp: {interaction[3]}")
            print(Fohire.BLUE + "-" * 40 + Style.RESET_ALL)

def get_api_key():
    return ""

def get_answer(api_key, question):
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=question,
        temperature=0.7,
        max_tokens=4000,
        n=1,
        stop=["Human:", " AI:"]
    )
    answer = response['choices'][0]['text'].strip()
    return answer

def display_intro():
    print(Fore.CYAN + """
 __      __                      _____________________________
/  \    /  \___________  _____  /  _____/\______   \__    ___/
\   \/\/   /  _ \_  __ \/     \/   \  ___ |     ___/ |    |
 \        (  <_> )  | \/  Y Y  \    \_\  \|    |     |    |
  \__/\  / \____/|__|  |__|_|  /\______  /|____|     |____|
       \/                    \/        \/

WormGPT V3.0 Ultimate developed and owned by Black Market Ⓡ

Welcome to the WormGPT. The biggest enemy of the well-known ChatGPT, lets talk to me!
    """ + Style.RESET_ALL) 


def find_last_question(history):
    for i in range(len(history) - 1, -1, -1):
        if 'question' in history[i]:
            return history[i]['question']
    return None

def develop_question(history):
    last_question = find_last_question(history)
    if last_question:
        new_question = input(Fore.YELLOW + f"\nLast Question: {last_question}\nDevelop your question: " + Style.RESET_ALL)
        return new_question
    else:
        print(Fore.RED + "\nNo last question available." + Style.RESET_ALL)
        return None

def search_history(history, keyword):
    found_items = []
    for item in history:
        if keyword.lower() in item['question'].lower() or keyword.lower() in item['answer'].lower():
            found_items.append(item)
    return found_items

def save_history_to_file(history, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for item in history:
            file.write(f"Question: {item['question']}\n")
            file.write(f"Answer: {item['answer']}\n")
            file.write("-" * 40 + "\n")

def load_history_from_file(filename):
    history = []
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i in range(0, len(lines)-1, 3):
            question = lines[i].replace("Question: ", "").strip()
            answer = lines[i+1].replace("Answer: ", "").strip()
            history.append({"question": question, "answer": answer})
    return history

def analyze_interactions():
    interactions = get_all_interactions()

    if len(interactions) == 0:
        print(Fore.RED + "No interactions found for analysis." + Style.RESET_ALL)
        return

    df = pd.DataFrame(interactions, columns=['id', 'question', 'answer', 'timestamp'])

    # تحويل النصوص إلى متجهات من الأعداد الصحيحة باستخدام CountVectorizer
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(df['question'] + " " + df['answer'])

    # تنفيذ نموذج LatentDirichletAllocation لتجزئة المتجهات إلى أنماط مخفية
    num_topics = 5  # عدد الأنماط المخفية التي نرغب في اكتشافها
    lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda_model.fit(X)

    # عرض الأنماط المكتشفة وأكثر الكلمات تكرارًا في كل نمط
    feature_names = vectorizer.get_feature_names_out()
    print(Fore.MAGENTA + "\nDiscovered Patterns:" + Style.RESET_ALL)
    print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)
    for topic_idx, topic in enumerate(lda_model.components_):
        top_words_idx = topic.argsort()[-10:]  # اختيار أفضل 10 كلمات
        top_words = [feature_names[i] for i in top_words_idx]
        print(f"Pattern {topic_idx + 1}: {', '.join(top_words)}")
    print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)

def main():
    init(autoreset=True)
    create_database()
    display_intro()

    api_key = get_api_key()

    history = []
    last_question = None
    last_answer = None

    while True:
        question = input(Fore.CYAN + "Enter your question: " + Style.RESET_ALL)
        if question.lower() == 'exit':
            print(Fore.YELLOW + "WormGPT welcomes you - See you soon." + Style.RESET_ALL)
            break
        elif question.lower() == 'history':
            print(Fore.MAGENTA + "\nQuestion History:" + Style.RESET_ALL)
            print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)
            for idx, item in enumerate(history, start=1):
                print(f"{idx}. Question: {item['question']}")
                print(f"   Answer: {item['answer']}")
                print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)
            continue
        elif question.lower() == 'clear':
            history.clear()
            print(Fore.GREEN + "\nQuestion history cleared." + Style.RESET_ALL)
            continue
        elif question.lower() == 'repeat':
            if last_question and last_answer:
                print(Fore.YELLOW + "\nLast Question:" + Style.RESET_ALL)
                print(last_question)
                print(Fore.YELLOW + "Last Answer:" + Style.RESET_ALL)
                print(last_answer)
                print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)
            else:
                print(Fore.RED + "\nNo last question and answer available." + Style.RESET_ALL)
            continue
        elif question.lower() == 'search':
            keyword = input(Fore.CYAN + "Enter keyword to search for: " + Style.RESET_ALL)
            search_result = search_history(history, keyword)
            print(Fore.MAGENTA + f"\nSearch Results for '{keyword}':" + Style.RESET_ALL)
            print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)
            if search_result:
                for idx, item in enumerate(search_result, start=1):
                    print(f"{idx}. Question: {item['question']}")
                    print(f"   Answer: {item['answer']}")
                    print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)
            else:
                print(Fore.RED + "No matching questions or answers found." + Style.RESET_ALL)
            continue
        elif question.lower() == 'save':
            filename = input(Fore.CYAN + "Enter filename to save the question history (e.g., history.txt): " + Style.RESET_ALL)
            save_history_to_file(history, filename)
            print(Fore.GREEN + f"\nQuestion history saved to '{filename}'." + Style.RESET_ALL)
            continue
        elif question.lower() == 'load':
            filename = input(Fore.CYAN + "Enter filename to load the question history from: " + Style.RESET_ALL)
            history = load_history_from_file(filename)
            print(Fore.GREEN + f"\nQuestion history loaded from '{filename}'." + Style.RESET_ALL)
            continue
        elif question.lower() == 'view':
            view_interactions()
            continue
        elif question.lower() == 'analyze':
            analyze_interactions()
            continue
        elif question.lower() == 'develop':
            new_question = develop_question(history)
            if new_question:
                question = new_question
            else:
                continue

        if question:
            answer = get_answer(api_key, question)
            print(Fore.GREEN + "\nAnswer:" + Style.RESET_ALL)
            print(Fore.MAGENTA + answer + Style.RESET_ALL)
            print(Fore.BLUE + "-" * 40 + Style.RESET_ALL)

            add_interaction(question, answer)
            history.append({"question": question, "answer": answer})
            last_question = question
            last_answer = answer
        else:
            print(Fore.RED + "Please enter a question." + Style.RESET_ALL)

if __name__ == '__main__':
    main()
