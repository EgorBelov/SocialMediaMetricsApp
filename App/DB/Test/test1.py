import psycopg2
from deap import base, creator, tools
import random

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    database="SocialMediaMetrics",
    user="postgres",
    password="123321",
    host="localhost",
    port="5432"
)

# Создание курсора
cursor = conn.cursor()

# Выполнение запроса для получения данных из таблицы
cursor.execute("SELECT id, avg_likes_on_photos, likes_on_wall, comments_on_wall, reposts_on_wall, count_friends, count_followers, popularity_score FROM public.vk_users")

# Извлечение данных
rows = cursor.fetchall()

# Определение функции цели
def calculate_popularity_score(params):
    avg_likes_on_photos, likes_on_wall, comments_on_wall, reposts_on_wall, count_friends, count_followers = params
    # Пример функции цели (веса параметров могут быть изменены)
    popularity_score = (
        0.2 * avg_likes_on_photos +
        0.3 * likes_on_wall +
        0.2 * comments_on_wall +
        0.2 * reposts_on_wall +
        0.1 * count_friends +
        0.1 * count_followers
    )
    return popularity_score

# Создание индивида и популяции
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=6)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Определение функции оценки (функции цели)
def evaluate(individual):
    params = tuple(individual)
    return calculate_popularity_score(params),

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# Генерация начальной популяции
population = toolbox.population(n=50)

# Запуск эволюционного процесса
gen = 0
while gen < 10:  # Замените это условие на критерии остановки
    # Оценка популяции
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    # Выбор следующего поколения
    offspring = toolbox.select(population, len(population))
    offspring = list(map(toolbox.clone, offspring))

    # Скрещивание и мутация
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.5:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    for mutant in offspring:
        if random.random() < 0.2:
            toolbox.mutate(mutant)
            del mutant.fitness.values

    # Замена старого на новое поколение
    population[:] = offspring

    # Вывод лучшего индивида и его значение функции цели
    best_ind = tools.selBest(population, 1)[0]
    best_params = tuple(best_ind)
    best_score = calculate_popularity_score(best_params)

    print(f"Generation {gen+1}: Best Score - {best_score}, Best Parameters - {best_params}")

    # Увеличение номера поколения
    gen += 1

# Закрытие соединения
cursor.close()
conn.close()
