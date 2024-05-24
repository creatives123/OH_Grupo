import pandas as pd
import openpyxl

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

# Função para calcular o "score" dos enfermeiros para cada procedimento
def calcular_score(tempos, categoria):
    if categoria in [2, 3]:
        return [tempo * 1.25 if tempo != 999 else 999 for tempo in tempos]
    return tempos

# Função para obter os três melhores enfermeiros para um procedimento
def obter_melhores_enfermeiros(procedimento, periodo, alocacoes):
    candidatos = []
    for e, tempos in tempos_procedimentos.items():
        if categorias[e] == 1 and procedimento['tipo'] == 'complexo':
            continue
        if len(alocacoes[e]) < 5 and all(p['periodo'] != periodo for p in alocacoes[e]):
            score = calcular_score(tempos, categorias[e])
            candidatos.append((e, score[procedimento['periodo'] - 1], tempos[procedimento['periodo'] - 1]))
    candidatos.sort(key=lambda x: x[1])
    return [c for c in candidatos[:3] if c[1] != 999]

# Inicializar alocações
alocacoes = {e: [] for e in tempos_procedimentos}
duracao_total = 0

# Alocar enfermeiros aos procedimentos
for p, dados_p in procedimentos.items():
    periodo = dados_p['periodo']
    melhores = obter_melhores_enfermeiros(dados_p, periodo, alocacoes)
    for e, _, tempo in melhores:
        alocacoes[e].append({'procedimento': p, 'periodo': periodo, 'tempo': tempo})

# Calcular a duração total e os tempos de cada procedimento
duracoes_periodos = []
tempos_procedimentos_max = {p: 0 for p in procedimentos}

for periodo in range(1, 8):
    duracoes = []
    for e, aloc in alocacoes.items():
        for proc in aloc:
            if proc['periodo'] == periodo:
                duracoes.append(proc['tempo'])
                if proc['tempo'] > tempos_procedimentos_max[proc['procedimento']]:
                    tempos_procedimentos_max[proc['procedimento']] = proc['tempo']
    duracao_periodo = max(duracoes) if duracoes else 0
    duracoes_periodos.append(duracao_periodo)
    duracao_total += duracao_periodo

# Verificar se a duração total ultrapassa as 8 horas
if duracao_total > 480:
    print("A duração total do dia de trabalho ultrapassa 8 horas. Ajustes necessários.", duracao_total)
else:
    print("Solução admissível encontrada. Duração total:", duracao_total, "minutos")

# Organizar as alocações por períodos
alocacoes_por_periodo = {i: [] for i in range(1, 8)}
for e, aloc in alocacoes.items():
    for proc in aloc:
        alocacoes_por_periodo[proc['periodo']].append({
            'enfermeiro': e,
            'procedimento': proc['procedimento'],
            'tempo': proc['tempo']
        })

# Escrever as alocações organizadas por períodos e tempos de cada procedimento em um arquivo txt
with open('alocacoes.txt', 'w') as f:
    f.write("Alocações por períodos:\n")
    for periodo, alocacoes in alocacoes_por_periodo.items():
        f.write(f"Período {periodo}:\n")
        for aloc in alocacoes:
            f.write(f"  - Enfermeiro: {aloc['enfermeiro']}, Procedimento: {aloc['procedimento']}, Tempo: {aloc['tempo']} minutos\n")
        f.write(f"Duração do Período: {duracoes_periodos[periodo - 1]} minutos\n")
    f.write("\nTempos de cada procedimento:\n")
    for p, tempo in tempos_procedimentos_max.items():
        f.write(f"Procedimento {p}: {tempo} minutos\n")