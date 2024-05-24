from time import sleep

import pandas as pd
import openpyxl
import random


file_path = 'Trab_Grupo.xlsx'  # Substitua pelo caminho do seu arquivo Excel

# Ler o arquivo Excel
df = pd.read_excel(file_path, header=0)

# Ajustar a leitura dos tempos dos enfermeiros
tempos_procedimentos = {
    f'E{int(df.columns[i]) + 1}': df.iloc[:, i].tolist() for i in range(df.shape[1])
}

# Categorias dos enfermeiros
categorias = {
    'E1': 1, 'E2': 1, 'E3': 1, 'E4': 1,
    'E5': 2, 'E6': 2, 'E7': 2, 'E8': 2,
    'E9': 3, 'E10': 3
}

procedimentos = {
    'P1': {'periodo': 1, 'tipo': 'regular'},
    'P2': {'periodo': 1, 'tipo': 'regular'},
    'P3': {'periodo': 2, 'tipo': 'complexo'},
    'P4': {'periodo': 2, 'tipo': 'regular'},
    'P5': {'periodo': 3, 'tipo': 'regular'},
    'P6': {'periodo': 3, 'tipo': 'regular'},
    'P7': {'periodo': 4, 'tipo': 'complexo'},
    'P8': {'periodo': 4, 'tipo': 'complexo'},
    'P9': {'periodo': 5, 'tipo': 'regular'},
    'P10': {'periodo': 5, 'tipo': 'complexo'},
    'P11': {'periodo': 6, 'tipo': 'regular'},
    'P12': {'periodo': 6, 'tipo': 'complexo'},
    'P13': {'periodo': 7, 'tipo': 'regular'},
    'P14': {'periodo': 7, 'tipo': 'regular'}
}

# Variáveis iniciais
enfermeiros_workload = {enf: 0 for enf in categorias.keys()}
max_per_proc = 5
max_duration = 8 * 60  # 8 horas em minutos
total_duration = 0
distribution = {period: [] for period in range(1, 8)}


# Função para calcular a duração de um procedimento
def calculate_duration(procedure, enfermeiros_selected):
    tempos = [tempos_procedimentos[enf][procedure - 1] for enf in enfermeiros_selected]
    return max(tempos)


# Atribuir enfermeiros aos procedimentos complexos
def assign_complex_procedures():
    total_duration = 0
    enfermeiros_workload = {enf: 0 for enf in categorias.keys()}
    distribution = {period: [] for period in range(1, 8)}

    for proc, details in procedimentos.items():
        if details['tipo'] == 'complexo':
            available_enfermeiros = [enf for enf, cat in categorias.items() if
                                     cat in [2, 3] and enfermeiros_workload[enf] < max_per_proc]
            if len(available_enfermeiros) < 3:
                raise Exception(f"Não há enfermeiros suficientes disponíveis para o procedimento {proc}.")
            selected_enfermeiros = random.sample(available_enfermeiros, 3)
            duration = calculate_duration(int(proc[1:]), selected_enfermeiros)

            if total_duration + duration > max_duration:
                raise Exception("Duração total excede as 8 horas.")

            distribution[details['periodo']].append((proc, selected_enfermeiros))
            total_duration += duration
            for enf in selected_enfermeiros:
                enfermeiros_workload[enf] += 1

    return distribution, total_duration, enfermeiros_workload


# Atribuir enfermeiros aos procedimentos regulares
def assign_regular_procedures(distribution, total_duration, enfermeiros_workload):
    for proc, details in procedimentos.items():
        if details['tipo'] == 'regular':
            available_enfermeiros = [enf for enf in categorias.keys() if enfermeiros_workload[enf] < max_per_proc]
            if len(available_enfermeiros) < 3:
                raise Exception(f"Não há enfermeiros suficientes disponíveis para o procedimento {proc}.")
            selected_enfermeiros = random.sample(available_enfermeiros, 3)
            duration = calculate_duration(int(proc[1:]), selected_enfermeiros)

            if total_duration + duration > max_duration:
                raise Exception("Duração total excede as 8 horas. Tempo: ", total_duration + duration , " minutos.")

            # Garantir que os enfermeiros não são duplicados dentro do mesmo período
            while any(
                    enf in [e for p in distribution[details['periodo']] for e in p[1]] for enf in selected_enfermeiros):
                selected_enfermeiros = random.sample(available_enfermeiros, 3)

            distribution[details['periodo']].append((proc, selected_enfermeiros))
            total_duration += duration
            for enf in selected_enfermeiros:
                enfermeiros_workload[enf] += 1

    return distribution, total_duration


# Loop até encontrar uma solução válida
solution_found = False
while not solution_found:
    try:
        distribution, total_duration, enfermeiros_workload = assign_complex_procedures()
        distribution, total_duration = assign_regular_procedures(distribution, total_duration, enfermeiros_workload)
        solution_found = True
    except Exception as e:
        print(e)
        continue

# Verificar a distribuição e a duração total
print(f"Duração total do dia de trabalho: {total_duration} minutos")
print(f"Distribuição: {distribution}")
print(f"Carga de trabalho dos enfermeiros: {enfermeiros_workload}")