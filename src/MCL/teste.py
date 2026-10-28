import simulador_fornecido as sim


while True:
    dado = sim.obter_proximo_movimento()
    if not dado:
        break    
    print(dado)



