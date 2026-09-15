import random 
import math



# inicialização: ageração das particulas

def criar_particulas(n_particulas):

    particulas = [{'x':random.uniform(-3,3),'y':random.uniform(-2,2),'theta':random.uniform(-math.pi,math.pi),'w': 1/n_particulas} for x in range(n_particulas)]

    # for x in range(n_particulas):
    #     p = {
    #         'x':random.uniform(-3,3),
    #         'y':random.uniform(-2,2),
    #         'theta':random.uniform(-math.pi,math.pi),
    #         'w': 1/n_particulas
    #     }
    #     particulas.append(p)

    return particulas

# predição: aplicação do modelo de transição

def aplicar_movimento(particula):

    for p in particula:
        p['x'] += math.



COMANDOS_TESTE = [
    ("avancar", 0.40),
    ("avancar", 0.40),
    ("girar", radians(20.0)),
    ("avancar", 0.40),
    ("avancar", 0.40),
    ("girar", radians(20.0)),
    ("avancar", 0.40),
    ("girar", radians(20.0)),
    ("avancar", 0.40),
]