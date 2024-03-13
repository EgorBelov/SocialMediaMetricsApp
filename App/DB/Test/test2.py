class User:
    def __init__(self, user_id, first_name, last_name, friends=None):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.friends = friends if friends is not None else []

    def add_friend(self, friend_id):
        self.friends.append(friend_id)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.user_id})"


import networkx as nx
import random
import copy

# Пример пользователей и их друзей
users_data = {
    1: [2, 3, 4],
    2: [1, 3],
    3: [1, 2, 4],
    4: [1, 3]
}

# Создание графа и добавление пользователей с их друзьями
G = nx.Graph()
for user_id, friends in users_data.items():
    G.add_node(user_id)
    G.add_edges_from((user_id, friend) for friend in friends)

def fitness_function(selected_users):
    # Рассчитываем сумму центральностей посредничества для выбранных пользователей
    total_betweenness = sum(nx.betweenness_centrality(G)[user_id] for user_id in selected_users)
    return total_betweenness

def genetic_algorithm(population_size, generations, mutation_rate):
    # Инициализация начальной популяции
    population = [random.sample(list(users_data.keys()), k=random.randint(1, len(users_data))) for _ in range(population_size)]

    for generation in range(generations):
        # Оценка приспособленности каждого индивида в популяции
        fitness_scores = [fitness_function(individual) for individual in population]

        # Выбор лучших индивидов
        elite_indices = sorted(range(population_size), key=lambda i: fitness_scores[i], reverse=True)[:int(0.2 * population_size)]
        elite_population = [population[i] for i in elite_indices]

        # Скрещивание (кроссовер) лучших индивидов
        new_population = []
        while len(new_population) < population_size - len(elite_population):
            parent1, parent2 = random.sample(elite_population, k=2)
            crossover_point = random.randint(1, min(len(parent1), len(parent2)) - 1)
            child = parent1[:crossover_point] + parent2[crossover_point:]
            new_population.append(child)

        # Мутация
        for i in range(len(new_population)):
            if random.random() < mutation_rate:
                mutation_point = random.randint(0, len(new_population[i]) - 1)
                new_population[i][mutation_point] = random.choice(list(users_data.keys()))


        # Объединение лучших индивидов и новых потомков
        population = elite_population + new_population

    # Возврат лучшего индивида
    best_individual = max(population, key=lambda ind: fitness_function(ind))
    return best_individual

# Пример использования генетического алгоритма
best_individual = genetic_algorithm(population_size=50, generations=100, mutation_rate=0.1)
print("Лучший индивид:", best_individual)
print("Значение приспособленности:", fitness_function(best_individual))

