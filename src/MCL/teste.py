import simulador_fornecido as sim

dado = sim.obter_proximo_movimento()

obs = sim.obter_observacao_mcl(dado['numero'])
print(obs)





