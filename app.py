import streamlit as st
import json
from supabase import create_client, Client

# --- НАСТРОЙКИ БАЗЫ ДАННЫХ SUPABASE ---
# Вставь сюда свои данные из Шага 1
SUPABASE_URL = "https://ktilsbsqrqagixtwolwp.supabase.co"
SUPABASE_KEY = "sb_publishable_Zsl9UySCnwR9VRmQKtIuow_9hNkRPbC"


# Инициализируем подключение
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_connection()

# Настройки страницы
st.set_page_config(page_title="ЄДКІ Кібербезпека", page_icon="🛡️")


@st.cache_data(ttl=30)
def load_questions():
    with open('questions.json', 'r', encoding='utf-8') as f:
        return json.load(f)


questions = load_questions()

# --- БОКОВАЯ ПАНЕЛЬ: АВТОРИЗАЦИЯ ---
st.sidebar.title("🔐 Авторизація")
student_id = st.sidebar.text_input("Введіть ваш ID або Нікнейм:")

# Если пользователь не ввел ID, просим его это сделать и останавливаем код
if not student_id:
    st.title("🛡️ Підготовка до ЄДКІ: Кібербезпека")
    st.info("👈 Будь ласка, введіть ваш ID у бічному меню зліва, щоб розпочати та зберігати прогрес.")
    st.stop()


# --- ЛОГИКА СОХРАНЕНИЯ ПРОГРЕССА В БАЗУ ---
# Функция для получения прогресса
def fetch_progress(user_id):
    response = supabase.table('user_progress').select('current_q').eq('student_id', user_id).execute()
    if len(response.data) > 0:
        return response.data[0]['current_q']
    else:
        # Если пользователя нет в базе, создаем его с 0 вопросом
        supabase.table('user_progress').insert({'student_id': user_id, 'current_q': 0}).execute()
        return 0


# Функция для обновления прогресса
def update_progress(user_id, new_q_index):
    supabase.table('user_progress').update({'current_q': new_q_index}).eq('student_id', user_id).execute()


# Инициализируем прогресс для текущего пользователя
if 'current_q' not in st.session_state or st.session_state.get('logged_in_user') != student_id:
    st.session_state.current_q = fetch_progress(student_id)
    st.session_state.logged_in_user = student_id

# --- ОСНОВНОЙ ИНТЕРФЕЙС ТЕСТА ---
st.title(f"👋 Привіт, {student_id}!")
st.write("---")

q = questions[st.session_state.current_q]

st.subheader(f"Питання {st.session_state.current_q + 1} з {len(questions)}")
st.write(f"**{q['question']}**")

user_choice = st.radio("Оберіть правильний варіант:", q['options'], index=None)

if st.button("Перевірити відповідь"):
    if user_choice is None:
        st.warning("Будь ласка, оберіть варіант відповіді!")
    else:
        user_index = q['options'].index(user_choice)
        correct_val = q['correct_index']

        if isinstance(correct_val, int):
            real_correct_index = correct_val
        else:
            letter_mapping = {'А': 0, 'Б': 1, 'В': 2, 'Г': 3, 'Д': 4}
            clean_letter = str(correct_val).strip().upper()
            real_correct_index = letter_mapping.get(clean_letter, 0)

        if user_index == real_correct_index:
            st.success("✅ Правильно!")
        else:
            st.error(f"❌ Помилка! Правильна відповідь: {q['options'][real_correct_index]}")

        st.info(f"**Пояснення:** {q['explanation']}")

st.write("---")

col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Попереднє питання") and st.session_state.current_q > 0:
        st.session_state.current_q -= 1
        update_progress(student_id, st.session_state.current_q)
        st.rerun()
with col2:
    if st.button("Наступне питання ➡️") and st.session_state.current_q < len(questions) - 1:
        st.session_state.current_q += 1
        update_progress(student_id, st.session_state.current_q)
        st.rerun()
