import streamlit as st
import json

# Настраиваем внешний вид страницы
st.set_page_config(page_title="ЄДКІ Кібербезпека", page_icon="🛡️")


# Функция для загрузки вопросов из файла
@st.cache_data
def load_questions():
    with open('questions1.json', 'r', encoding='utf-8') as f:
        return json.load(f)


questions = load_questions()

# Инициализируем переменную в сессии для отслеживания номера вопроса
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0

st.title("🛡️ Підготовка до ЄДКІ: Кібербезпека")
st.write("---")

# Получаем текущий вопрос
q = questions[st.session_state.current_q]

# Выводим текст вопроса
st.subheader(f"Питання {st.session_state.current_q + 1} з {len(questions)}")
st.write(f"**{q['question']}**")

# Выводим варианты ответов
user_choice = st.radio("Оберіть правильний варіант:", q['options'], index=None)

# Кнопка проверки
if st.button("Перевірити відповідь"):
    if user_choice is None:
        st.warning("Будь ласка, оберіть варіант відповіді!")
    else:
        # Знаходимо порядковий номер відповіді користувача
        user_index = q['options'].index(user_choice)

        # --- НОВА ЛОГІКА РОЗПІЗНАВАННЯ ---
        correct_val = q['correct_index']

        # Перевіряємо: якщо це вже цифра (як у моїх питаннях) - залишаємо як є
        if isinstance(correct_val, int):
            real_correct_index = correct_val
        else:
            # Якщо це буква (як у перших 100), переводимо її в цифру
            letter_mapping = {'А': 0, 'Б': 1, 'В': 2, 'Г': 3, 'Д': 4}
            # Очищаємо від пробілів, робимо великою і шукаємо в словнику
            clean_letter = str(correct_val).strip().upper()
            real_correct_index = letter_mapping.get(clean_letter, 0)

        # Тепер порівнюємо дві цифри
        if user_index == real_correct_index:
            st.success("✅ Правильно!")
        else:
            st.error(f"❌ Помилка! Правильна відповідь: {q['options'][real_correct_index]}")

        # Виводимо пояснення
        st.info(f"**Пояснення:** {q['explanation']}")

st.write("---")

# Кнопки навигации
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ Попереднє питання") and st.session_state.current_q > 0:
        st.session_state.current_q -= 1
        st.rerun()
with col2:
    if st.button("Наступне питання ➡️") and st.session_state.current_q < len(questions) - 1:
        st.session_state.current_q += 1
        st.rerun()