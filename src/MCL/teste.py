import simulador_fornecido as sim


dado = sim.obter_proximo_movimento()    
print(dado)
obs = sim.obter_observacao(dado['numero'])
obs_mcl = sim.obter_observacao_mcl(dado['numero'])

print('x',dado['comando']['linear']['x'])
print('y',dado['comando']['linear']['y'])
print('z',dado['comando']['angular']['z'])
print('dt',dado['dt'])