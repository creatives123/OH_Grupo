from matplotlib import pyplot as plt
import pandas as pd
import random

# Carregar os dados do Excel
file_path = 'Trab_Grupo.xlsx'
df = pd.read_excel(file_path)

NUM_PROCEDURES = 14
NUM_NURSES = 10
MAX_NURSES_PER_PROCEDURE = 3
POPULATION_SIZE = 50
GENERATIONS = 3000
CROSSOVER_TYPE = 'multi-point'  # multi-point, uniform
CROSSOVER_POINT_K = 5
SELECTION_TYPE = 'tournament'  # tournament, fitness-proportional, rank, random
MUTATION_TYPE = 'bit_flip'  # 'bit_flip', 'swap', 'inversion'
MUTATION_RATE = 0.1


# Categorias dos enfermeiros
categorias = {
    'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1,
    'E5': 2, 'E6': 2, 'E7': 2, 'E8': 2,
    'E9': 3, 'E10': 3
}

# Enfermeiros da categoria 1
enfermeiros_categoria_1 = {0, 1, 2, 3}

# Procedimentos que não podem ser realizados por enfermeiros da categoria 1
procedimentos_restritos = {2, 6, 7, 9, 11}


# Função de avaliação de fitness
def evaluate_fitness(cromossoma):
    fitness = 0
    enfermeiro_count = [0] * NUM_NURSES
    total_duration = 0

    # Period pairs as given in the assignment
    period_pairs = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]

    max_times = [[df.iloc[i, enfermeiro] for enfermeiro in procedimento] for i, procedimento in enumerate(cromossoma)]

    for p1, p2 in period_pairs:
        procedimento1 = cromossoma[p1]
        procedimento2 = cromossoma[p2]

        if len(set(procedimento1 + procedimento2)) != 6:
            fitness += 1000  # Penalidade alta para enfermeiros repetidos no mesmo período

        duration1 = max(max_times[p1])
        duration2 = max(max_times[p2])

        period_duration = max(duration1, duration2)
        total_duration += period_duration
        fitness += period_duration

        for enfermeiro in procedimento1 + procedimento2:
            enfermeiro_count[enfermeiro] += 1

            # Penalizar enfermeiro que participa mais de 5 vezes
            if enfermeiro_count[enfermeiro] > 5:
                fitness += 250  # Penalidade alta

        # Penalizar uso de enfermeiros da categoria 1 em procedimentos restritos
        if p1 in procedimentos_restritos and any(enfermeiro in enfermeiros_categoria_1 for enfermeiro in procedimento1):
            fitness += 1000
        if p2 in procedimentos_restritos and any(enfermeiro in enfermeiros_categoria_1 for enfermeiro in procedimento2):
            fitness += 1000

    # Bônus para soluções com fitness < 460
    if fitness < 460:
        fitness -= 200

    return -fitness, total_duration  # Queremos minimizar a duração total com penalidades


# Seleção por torneio
def tournament_selection(population, k=6):
    selected = random.sample(population, k)
    selected.sort(key=lambda x: evaluate_fitness(x), reverse=True)
    return selected[0]


# Seleção proporcional ao fitness
def fitness_proportional_selection(population):
    fitness_scores = [evaluate_fitness(individual)[0] for individual in population]
    total_fitness = sum(fitness_scores)
    probabilities = [fitness / total_fitness for fitness in fitness_scores]

    selected = random.choices(population, weights=probabilities, k=1)[0]
    return selected


# Seleção por ranking
def rank_selection(population):
    sorted_population = sorted(population, key=lambda x: evaluate_fitness(x)[0], reverse=True)
    rank_weights = [1 / (i + 1) for i in range(len(sorted_population))]

    selected = random.choices(sorted_population, weights=rank_weights, k=1)[0]
    return selected


# Seleção aleatória
def random_selection(population):
    selected = random.choice(population)
    return selected


# Operador de crossover de K pontos
def multi_point_crossover(parent1, parent2, num_points=5):
    # Garante que não haja duplicação de pontos de crossover
    points = sorted(random.sample(range(1, len(parent1)), num_points))

    # Inicializa os filhos com cópias dos pais
    child1, child2 = parent1[:], parent2[:]

    # Alterna segmentos entre os pais
    for i in range(len(points)):
        if i % 2 == 0:
            child1[points[i]:points[i + 1] if i + 1 < len(points) else None], \
                child2[points[i]:points[i + 1] if i + 1 < len(points) else None] = \
                parent2[points[i]:points[i + 1] if i + 1 < len(points) else None], \
                parent1[points[i]:points[i + 1] if i + 1 < len(points) else None]

    return child1, child2


# Operador de crossover uniforme
def uniform_crossover(parent1, parent2):
    child1 = []
    child2 = []

    for i in range(NUM_PROCEDURES):
        if random.random() < 0.5:
            child1.append(parent1[i])
            child2.append(parent2[i])
        else:
            child1.append(parent2[i])
            child2.append(parent1[i])

    return child1, child2


# Operador de mutação (Bit Flip)
def mutate(cromossoma, mutation_rate):
    for i in range(len(cromossoma)):
        if random.random() < mutation_rate:
            if MUTATION_TYPE == 'bit_flip':
                cromossoma[i] = bit_flip_mutation(cromossoma[i])
            elif MUTATION_TYPE == 'swap':
                cromossoma = swap_mutation(cromossoma)
            elif MUTATION_TYPE == 'inversion':
                cromossoma = inversion_mutation(cromossoma)
    return cromossoma


# Mutação Bit Flip - Muda um enfermeiro aleatório da Tupla
def bit_flip_mutation(procedure):
    enfermeiros = list(procedure)
    enfermeiro_idx = random.randint(0, MAX_NURSES_PER_PROCEDURE - 1)  # Escolhe aleatoriamente um dos três enfermeiros
    while True:
        new_enfermeiro = random.randint(0, NUM_NURSES - 1)
        if new_enfermeiro != enfermeiros[enfermeiro_idx]:
            enfermeiros[enfermeiro_idx] = new_enfermeiro
            break
    return tuple(enfermeiros)


# Mutação Swap - Troca dois enfermeiros aleatórios
def swap_mutation(cromossoma):
    idx1, idx2 = random.sample(range(len(cromossoma)), 2)
    cromossoma[idx1], cromossoma[idx2] = cromossoma[idx2], cromossoma[idx1]
    return cromossoma


# Mutação Inversão - Inverte a ordem dos enfermeiros entre dois pontos
def inversion_mutation(cromossoma):
    idx1, idx2 = sorted(random.sample(range(len(cromossoma)), 2))
    cromossoma[idx1:idx2] = reversed(cromossoma[idx1:idx2])
    return cromossoma


# Inicializar a população aleatória
def initialize_population(size):
    population = []
    for _ in range(size):
        individual = [
            (random.randint(0, NUM_NURSES - 1), random.randint(0, NUM_NURSES - 1), random.randint(0, NUM_NURSES - 1))
            for _ in range(NUM_PROCEDURES)]
        population.append(individual)
    return population


# Atualização da população
def evolve_population(population):
    new_population = []
    for _ in range(len(population) // 2):
        parent1 = None
        parent2 = None
        child1 = None
        child2 = None
        # Selecionar os pais conforme o método de seleção
        match SELECTION_TYPE:
            case 'tournament':
                parent1 = tournament_selection(population)
                parent2 = tournament_selection(population)
            case 'fitness-proportional':
                parent1 = fitness_proportional_selection(population)
                parent2 = fitness_proportional_selection(population)
            case 'rank':
                parent1 = rank_selection(population)
                parent2 = rank_selection(population)
            case 'random':
                parent1 = random_selection(population)
                parent2 = random_selection(population)

        match CROSSOVER_TYPE:
            case 'multi-point':
                child1, child2 = multi_point_crossover(parent1, parent2, CROSSOVER_POINT_K)
            case 'uniform':
                child1, child2 = uniform_crossover(parent1, parent2)

        child1 = mutate(child1, MUTATION_RATE)
        child2 = mutate(child2, MUTATION_RATE)
        new_population.extend([child1, child2])
    return new_population


def genetic_algorithm():
    population = initialize_population(POPULATION_SIZE - 1)
    best_fitness_over_generations = []
    best_duration_over_generations = []

    # Inicializar as variáveis para a melhor solução global
    global_best_fitness = float('-inf')
    global_best_duration = None
    global_best_solution = None

    for generation in range(GENERATIONS):
        population = evolve_population(population)
        for individual in population:
            fitness, duration = evaluate_fitness(individual)
            if fitness > global_best_fitness:
                global_best_fitness = fitness
                global_best_duration = duration
                global_best_solution = individual

        best_fitness_over_generations.append(global_best_fitness)
        best_duration_over_generations.append(global_best_duration)
        print(f'Geração {generation}: Melhor Fitness = {global_best_fitness}, Duração = {global_best_duration}')

    return global_best_solution, global_best_fitness, global_best_duration


# Executar o algoritmo genético
best_solution, best_fitness, best_duration = genetic_algorithm()

# Imprimir a melhor solução encontrada
print('Melhor solução encontrada:')
print(best_solution)
print(f'Melhor Fitness: {best_fitness}, Duração Total: {best_duration}')
