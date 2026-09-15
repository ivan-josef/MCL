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

def aplicar_movimento(particula,movimento):

    passo = 0.4
    erro_desloc = 0.05
    rot = 20.0
    erro_rot = 3

    desloc = passo + random.uniform(-erro_desloc,erro_desloc)

    if movimento == 'avancar':
        particula['x'] += (desloc  * math.cos(particula['theta'])) 
        particula['y'] += (desloc  * math.sin(particula['theta'])) 
    elif movimento == 'girar':
        particula['theta'] += math.radians(rot) + random.uniform(-math.radians(erro_rot),math.radians(erro_rot))

def mover_particulas(particulas,movimento):

    for p in particulas:
        aplicar_movimento(p,movimento)




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