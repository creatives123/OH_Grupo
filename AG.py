import pandas as pd
import random

# Carregar os dados do Excel
file_path = 'Trab_Grupo.xlsx'
df = pd.read_excel(file_path)

NUM_PROCEDURES = 14
NUM_NURSES = 10
POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.01

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
    (0, 1, 2), (3, 8, 9)   # P13, P14
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

# Operador de crossover de um ponto
def one_point_crossover(parent1, parent2):
    point = random.randint(1, NUM_PROCEDURES - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

# Operador de mutação (Bit Flip)
def mutate(cromossoma, mutation_rate):
    for i in range(len(cromossoma)):
        if random.random() < mutation_rate:
            cromossoma[i] = bit_flip_mutation(cromossoma[i], i)
    return cromossoma

# Mutação Bit Flip
def bit_flip_mutation(procedure, procedure_index):
    enfermeiros = list(procedure)
    enfermeiro_idx = random.randint(0, 2)  # Escolhe aleatoriamente um dos três enfermeiros
    while True:
        new_enfermeiro = random.randint(0, NUM_NURSES - 1)
        if new_enfermeiro != enfermeiros[enfermeiro_idx]:
            enfermeiros[enfermeiro_idx] = new_enfermeiro
            break
    # Garantir que os enfermeiros respeitam as restrições de categoria
    if procedure_index in procedimentos_restritos and any(enfermeiro in enfermeiros_categoria_1 for enfermeiro in enfermeiros):
        return bit_flip_mutation(procedure, procedure_index)  # Repetir até que a restrição seja satisfeita
    return tuple(enfermeiros)

# Gera um procedimento válido considerando as restrições
def generate_valid_procedure(procedure_index):
    while True:
        enfermeiros = (random.randint(0, NUM_NURSES-1), random.randint(0, NUM_NURSES-1), random.randint(0, NUM_NURSES-1))
        if (procedure_index in procedimentos_restritos and all(enfermeiro not in enfermeiros_categoria_1 for enfermeiro in enfermeiros)) or (procedure_index not in procedimentos_restritos):
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
        parent1 = tournament_selection(population)
        parent2 = tournament_selection(population)
        child1, child2 = one_point_crossover(parent1, parent2)
        child1 = mutate(child1, mutation_rate)
        child2 = mutate(child2, mutation_rate)
        new_population.extend([child1, child2])
    return new_population

# Função principal do algoritmo genético
def genetic_algorithm():
    population = [initial_solution] + initialize_population(POPULATION_SIZE - 1)
    for generation in range(GENERATIONS):
        population = evolve_population(population, MUTATION_RATE)
        best_fitness, best_duration = max((evaluate_fitness(individual) for individual in population), key=lambda x: x[0])
        print(f'Geração {generation}: Melhor Fitness = {best_fitness}, Duração = {best_duration}')

    best_solution = max(population, key=lambda x: evaluate_fitness(x)[0])
    best_fitness, best_duration = evaluate_fitness(best_solution)
    return best_solution, best_fitness, best_duration

# Executar o algoritmo genético
best_solution, best_fitness, best_duration = genetic_algorithm()
print('Melhor solução encontrada:')
print(best_solution)
print(f'Melhor Fitness: {best_fitness}, Duração Total: {best_duration}')

