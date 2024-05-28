import pandas as pd
import random

# Carregar os dados do Excel
file_path = 'Trab_Grupo.xlsx'
df = pd.read_excel(file_path)

NUM_PROCEDURES = 14
NUM_NURSES = 10
POPULATION_SIZE = 100
GENERATIONS = 500
MUTATION_RATE = 0.05

CROSSOVER_TYPE = 'two-point'  # one-point, two-point, uniform
SELECTION_TYPE = 'tournament'  # tournament, fitness-proportional, rank, random
MUTATION_TYPE = 'inversion'  # bit-flip, inversion, swap
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

# Cromossoma inicial fornecido
initial_solution = [
    (2, 3, 5), (1, 7, 9),  # P1, P2
    (4, 7, 8), (0, 1, 3),  # P3, P4
    (0, 1, 2), (4, 5, 9),  # P5, P6
    (6, 7, 8), (4, 5, 9),  # P7, P8
    (3, 4, 6), (5, 7, 8),  # P9, P10
    (2, 3, 7), (4, 5, 6),  # P11, P12
    (0, 1, 2), (3, 8, 9)  # P13, P14
]


# Função de avaliação de fitness
def evaluate_fitness(cromossoma):
    fitness = 0
    enfermeiro_count = [0] * NUM_NURSES
    total_duration = 0

    # Period pairs as given in the assignment
    period_pairs = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]

    for p1, p2 in period_pairs:
        procedimento1 = cromossoma[p1]
        procedimento2 = cromossoma[p2]

        if len(set(procedimento1 + procedimento2)) != 6:
            fitness += 1000  # Penalidade alta para enfermeiros repetidos no mesmo período

        times1 = [df.iloc[p1, enfermeiro] for enfermeiro in procedimento1]
        times2 = [df.iloc[p2, enfermeiro] for enfermeiro in procedimento2]

        duration1 = max(times1)
        duration2 = max(times2)

        period_duration = max(duration1, duration2)
        total_duration += period_duration
        fitness += period_duration

        for enfermeiro in procedimento1 + procedimento2:
            enfermeiro_count[enfermeiro] += 1

            # Penalizar enfermeiro que participa mais de 5 vezes
            if enfermeiro_count[enfermeiro] > 5:
                fitness += 1000  # Penalidade alta

        # Penalizar uso de enfermeiros da categoria 1 em procedimentos restritos
        if p1 in procedimentos_restritos and any(enfermeiro in enfermeiros_categoria_1 for enfermeiro in procedimento1):
            fitness += 1000  # Penalidade alta
        if p2 in procedimentos_restritos and any(enfermeiro in enfermeiros_categoria_1 for enfermeiro in procedimento2):
            fitness += 1000  # Penalidade alta

    return -fitness, total_duration  # Queremos minimizar a duração total com penalidades


# Seleção por torneio
def tournament_selection(population, k=3):
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


# Operador de crossover de um ponto
def one_point_crossover(parent1, parent2):
    point = random.randint(1, NUM_PROCEDURES - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


# Operador de crossover de dois pontos
def two_point_crossover(parent1, parent2):
    point1 = random.randint(1, NUM_PROCEDURES - 2)
    point2 = random.randint(point1 + 1, NUM_PROCEDURES - 1)

    child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
    child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]

    return child1, child2


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
            if MUTATION_TYPE == 'bit-flip':
                cromossoma[i] = bit_flip_mutation(cromossoma[i], i)
            elif MUTATION_TYPE == 'inversion':
                cromossoma[i] = inversion_mutation(cromossoma[i])
            elif MUTATION_TYPE == 'swap':
                cromossoma[i] = swap_mutation(cromossoma[i])
    return cromossoma


# Mutação Bit Flip
def bit_flip_mutation(procedure, procedure_index, max_attempts=100):
    enfermeiros = list(procedure)
    enfermeiro_idx = random.randint(0, 2)  # Escolhe aleatoriamente um dos três enfermeiros

    for attempt in range(max_attempts):
        new_enfermeiro = random.randint(0, NUM_NURSES - 1)
        if new_enfermeiro != enfermeiros[enfermeiro_idx]:
            enfermeiros[enfermeiro_idx] = new_enfermeiro

            # Verificar a restrição de categoria
            if procedure_index not in procedimentos_restritos or all(
                    enfermeiro not in enfermeiros_categoria_1 for enfermeiro in enfermeiros):
                return tuple(enfermeiros)

    # Se não encontrar uma mutação válida, retorna o procedimento original
    return procedure


# Mutação de inversão
def inversion_mutation(procedure):
    enfermeiros = list(procedure)
    i, j = sorted(random.sample(range(3), 2))  # Escolhe aleatoriamente dois índices diferentes para inversão
    enfermeiros[i:j+1] = reversed(enfermeiros[i:j+1])
    return tuple(enfermeiros)


# Mutação de troca
def swap_mutation(procedure):
    enfermeiros = list(procedure)
    i, j = random.sample(range(3), 2)  # Escolhe aleatoriamente dois índices diferentes para troca
    enfermeiros[i], enfermeiros[j] = enfermeiros[j], enfermeiros[i]
    return tuple(enfermeiros)


# Função de mutação (Bit Flip) revisada para usar a nova versão de bit_flip_mutation
def mutate(cromossoma, mutation_rate):
    for i in range(len(cromossoma)):
        if random.random() < mutation_rate:

            cromossoma[i] = bit_flip_mutation(cromossoma[i], i)
    return cromossoma


# Gera um procedimento válido considerando as restrições
def generate_valid_procedure(procedure_index):
    while True:
        enfermeiros = (
        random.randint(0, NUM_NURSES - 1), random.randint(0, NUM_NURSES - 1), random.randint(0, NUM_NURSES - 1))

        return enfermeiros


# Inicializar a população
def initialize_population(size):
    population = []
    for _ in range(size):
        individual = [generate_valid_procedure(i) for i in range(NUM_PROCEDURES)]
        population.append(individual)
    return population


# Atualização da população
def evolve_population(population, mutation_rate):
    new_population = []
    for _ in range(len(population) // 2):
        if SELECTION_TYPE == 'tournament':
            parent1 = tournament_selection(population, 10)
            parent2 = tournament_selection(population, 10)
        elif SELECTION_TYPE == 'fitness-proportional':
            parent1 = fitness_proportional_selection(population)
            parent2 = fitness_proportional_selection(population)
        elif SELECTION_TYPE == 'rank':
            parent1 = rank_selection(population)
            parent2 = rank_selection(population)
        elif SELECTION_TYPE == 'random':
            parent1 = random_selection(population)
            parent2 = random_selection(population)

        if CROSSOVER_TYPE == 'one-point':
            child1, child2 = one_point_crossover(parent1, parent2)
        elif CROSSOVER_TYPE == 'two-point':
            child1, child2 = two_point_crossover(parent1, parent2)
        elif CROSSOVER_TYPE == 'uniform':
            child1, child2 = uniform_crossover(parent1, parent2)

        child1 = mutate(child1, mutation_rate)
        child2 = mutate(child2, mutation_rate)
        new_population.extend([child1, child2])
    return new_population


# Função principal do algoritmo genético
def genetic_algorithm():
    old_fitness = 0
    count = 0
    MUTATION_RATE = 0.05
    population = initialize_population(POPULATION_SIZE)
    generation = 0
    best_duration = 999999
    while best_duration > 420:
        population = evolve_population(population, MUTATION_RATE)
        best_fitness, best_duration = max((evaluate_fitness(individual) for individual in population),
                                          key=lambda x: x[0])
        if best_fitness == old_fitness:
            count += 1
        else:
            count = 0
            MUTATION_RATE = 0.05
            old_fitness = best_fitness
        if count >= 20:
            MUTATION_RATE = 0.1
            print(f'Mutation rate increased to {MUTATION_RATE}')
        print(f'Geração {generation}: Melhor Fitness = {best_fitness}, Duração = {best_duration}')
        generation += 1

    best_solution = max(population, key=lambda x: evaluate_fitness(x)[0])
    best_fitness, best_duration = evaluate_fitness(best_solution)
    return best_solution, best_fitness, best_duration


# Executar o algoritmo genético
# Print Start time
print('Start Time')
start_time = pd.Timestamp.now()
print(start_time)
best_solution, best_fitness, best_duration = genetic_algorithm()
print('Melhor solução encontrada:')
print(best_solution)
print(f'Melhor Fitness: {best_fitness}, Duração Total: {best_duration}')
# Print End time
print('End Time')
end_time = pd.Timestamp.now()
print(end_time)
# Print Duration
print('Duration')
print(end_time - start_time)
