# Bibliotecas
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

isolamento = ctrl.Antecedent(np.arange(0, 101, 1), 'isolamento')
lubrificacao = ctrl.Antecedent(np.arange(0, 24001, 1), 'lubrificacao')
manutencao = ctrl.Antecedent(np.arange(0, 10000, 1), 'manutencao')
temperatura = ctrl.Antecedent(np.arange(-10, 51, 1), 'temperatura')
desq = ctrl.Antecedent(np.arange(0.0, 5.01, 0.01), 'desq')

risco_falha = ctrl.Consequent(np.arange(0, 101, 1), 'risco_falha')


def entrada_float(mensagem, min_val, max_val, unidade):
    while True:
        try:
            valor = float(input(mensagem))
            if not min_val <= valor <= max_val:
                print(f"Valor inválido: deve estar entre {min_val} e {max_val} {unidade}.")
                continue
            return valor
        except ValueError:
            print("Entrada inválida! Digite um número.")



# Funções de pertinência
isolamento['critico'] = fuzz.trimf(isolamento.universe, [0, 10, 20])
isolamento['aceitavel'] = fuzz.trimf(isolamento.universe, [20, 45, 70])
isolamento['ideal'] = fuzz.trimf(isolamento.universe, [70, 85, 100])

lubrificacao['baixo'] = fuzz.trimf(lubrificacao.universe, [5000, 9000, 12000])
lubrificacao['medio'] = fuzz.trimf(lubrificacao.universe, [12000, 15000, 18000])
lubrificacao['alto'] = fuzz.trimf(lubrificacao.universe, [18000, 20000, 24000])

manutencao['baixa'] = fuzz.trimf(manutencao.universe, [500, 1000, 2000])
manutencao['media'] = fuzz.trimf(manutencao.universe, [2001, 4000, 6000])
manutencao['alta'] = fuzz.trimf(manutencao.universe, [6001, 8000, 10000])

temperatura['baixa'] = fuzz.trimf(temperatura.universe, [-10, 0, 15])
temperatura['media'] = fuzz.trimf(temperatura.universe, [5, 20, 35])
temperatura['alta'] = fuzz.trimf(temperatura.universe, [25, 40, 50])

desq['aceitavel'] = fuzz.trapmf(desq.universe, [0.0, 1.0, 2.0, 3.0])
desq['alerta'] = fuzz.trapmf(desq.universe, [1.0, 2.0, 3.0, 4.0])
desq['critico'] = fuzz.trapmf(desq.universe, [2.0, 3.0, 4.0, 5.0])

risco_falha['baixo'] = fuzz.trapmf(risco_falha.universe, [0, 0, 25, 40])
risco_falha['medio'] = fuzz.trimf(risco_falha.universe, [35, 55, 70])
risco_falha['alto'] = fuzz.trapmf(risco_falha.universe, [65, 80, 100, 100])

rules = [
    # Regras críticas (alto risco)
    ctrl.Rule(isolamento['critico'] | temperatura['alta'] | desq['critico'], risco_falha['alto']),
    ctrl.Rule(lubrificacao['baixo'] & manutencao['baixa'], risco_falha['alto']),

    # Combinações de médio risco
    ctrl.Rule(isolamento['aceitavel'] & lubrificacao['medio'] & temperatura['media'], risco_falha['medio']),
    ctrl.Rule(manutencao['media'] & desq['alerta'], risco_falha['medio']),
    ctrl.Rule(lubrificacao['alto'] & temperatura['baixa'] & desq['aceitavel'], risco_falha['medio']),

    # Situações de baixo risco
    ctrl.Rule(isolamento['ideal'] & lubrificacao['alto'] & manutencao['alta'], risco_falha['baixo']),
    ctrl.Rule(temperatura['baixa'] & desq['aceitavel'] & isolamento['aceitavel'], risco_falha['baixo']),

    # Regras mistas
    ctrl.Rule(isolamento['aceitavel'] & (lubrificacao['medio'] | lubrificacao['alto']), risco_falha['medio']),
    ctrl.Rule(manutencao['alta'] & (temperatura['media'] | temperatura['baixa']), risco_falha['baixo']),
    ctrl.Rule(desq['alerta'] & ~isolamento['critico'] & ~temperatura['alta'], risco_falha['medio'])
]

# Sistema de controle
risco_ctrl = ctrl.ControlSystem(rules)
simulador = ctrl.ControlSystemSimulation(risco_ctrl)

simulador.input['isolamento'] = 85
simulador.input['lubrificacao'] = 15000
simulador.input['manutencao'] = 3000
simulador.input['temperatura'] = 25
simulador.input['desq'] = 2.5

simulador.compute()
print(f"Resultado de teste: Risco de Falha = {simulador.output['risco_falha']:.2f}")

# Função de interação
def regras_ativas_motor():
    try:
        # Entradas manuais
        isol = entrada_float("Resistência do isolamento elétrico (0 a 100 MΩ): ", 0, 100, "MΩ")
        lub = entrada_float("Qualidade da lubrificação (5.000 a 24.000 horas): ", 5000, 24000, "h")
        manu = entrada_float("Frequência de manutenção (500 a 10.000 horas): ", 500, 10000, "h")
        temp = entrada_float("Temperatura do enrolamento (-10 a 50 ºC): ", -10, 50, "ºC")
        desq_input = entrada_float("Desequilíbrio entre fases (0.0 a 5.0 %): ", 0.0, 5.0, "%")


        # Validação detalhada com mensagens específicas
        erros = []

        if not 0 <= isol <= 100:
            erros.append("Resistência do isolamento deve estar entre 0 e 100 MΩ")
        if not 5000 <= lub <= 24000:
            erros.append("Qualidade da lubrificação deve estar entre 5.000 e 24.000 horas")
        if not 500 <= manu <= 10000:
            erros.append("Frequência de manutenção deve estar entre 500 e 10.000 horas")
        if not -10 <= temp <= 50:
            erros.append("Temperatura do enrolamento deve estar entre -10 e 50 ºC")
        if not 0.0 <= desq_input <= 5.0:
            erros.append("Desequilíbrio entre fases deve estar entre 0.0 e 5.0 %")

        if erros:
            print("Erros de validação encontrados:")
            for erro in erros:
                print(f"- {erro}")
            return

        # Mostrar valores informados
        print(f"\nEntradas:")
        print(f"Resistência do isolamento elétrico: {isol} MΩ")
        print(f"Qualidade da lubrificação: {lub} h")
        print(f"Frequência de manutenção: {manu} h")
        print(f"Temperatura do enrolamento: {temp} ºC")
        print(f"Desequilíbrio entre fases: {desq_input} %")

        # Graus de pertinência
        print("\nGraus de pertinência (ativação dos conjuntos fuzzy):")

        print("→ Resistência do isolamento elétrico:")
        for termo in isolamento.terms:
            grau = fuzz.interp_membership(isolamento.universe, isolamento[termo].mf, isol)
            if grau > 0:
                print(f"   - {termo}: {grau:.2%}")

        print("→ Qualidade da lubrificação:")
        for termo in lubrificacao.terms:
            grau = fuzz.interp_membership(lubrificacao.universe, lubrificacao[termo].mf, lub)
            if grau > 0:
                print(f"   - {termo}: {grau:.2%}")

        print("→ Frequência de manutenção:")
        for termo in manutencao.terms:
            grau = fuzz.interp_membership(manutencao.universe, manutencao[termo].mf, manu)
            if grau > 0:
                print(f"   - {termo}: {grau:.2%}")

        print("→ Temperatura do enrolamento:")
        for termo in temperatura.terms:
            grau = fuzz.interp_membership(temperatura.universe, temperatura[termo].mf, temp)
            if grau > 0:
                print(f"   - {termo}: {grau:.2%}")

        print("→ Desequilíbrio entre fases:")
        for termo in desq.terms:
            grau = fuzz.interp_membership(desq.universe, desq[termo].mf, desq_input)
            if grau > 0:
                print(f"   - {termo}: {grau:.2%}")

        # Inserir valores no sistema fuzzy
        simulador.input['isolamento'] = isol
        simulador.input['lubrificacao'] = lub
        simulador.input['manutencao'] = manu
        simulador.input['temperatura'] = temp
        simulador.input['desq'] = desq_input

        # Computar o resultado
        simulador.compute()

        # Saída
        resultado = simulador.output['risco_falha']
        print(f"\nResultado fuzzy: Risco de Falha = {resultado:.2f}")

        # Exibição gráfica dos conjuntos fuzzy
        print("\nExibindo gráficos...")
        risco_falha.view(sim=simulador)

    except Exception as e:
        print(f"Erro: {e}")

regras_ativas_motor()