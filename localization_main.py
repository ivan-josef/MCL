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

    pos_old = particula.copy()
    desloc = passo + random.uniform(-erro_desloc,erro_desloc)

    if movimento == 'avancar':
        particula['x'] += (desloc  * math.cos(particula['theta'])) 
        particula['y'] += (desloc  * math.sin(particula['theta'])) 
    elif movimento == 'girar':
        particula['theta'] += math.radians(rot) + random.uniform(-math.radians(erro_rot),math.radians(erro_rot))

    c = 0
    if (particula['x'] < -3 or particula ['x'] > 3) or (particula['y'] < -2 or particula['y'] >2):
        while (particula['x'] < -3 or particula ['x'] > 3) or (particula['y'] < -2 or particula['y'] >2):
            particula['x'] = pos_old['x']
            particula['y'] = pos_old['y']
            desloc = passo + random.uniform(-erro_desloc,erro_desloc)
            particula['x'] += (desloc  * math.cos(particula['theta'])) 
            particula['y'] += (desloc  * math.sin(particula['theta'])) 
            c+=1
            if c >= 10:
                return pos_old

def mover_particulas(particulas,movimento):

    for p in particulas:
        aplicar_movimento(p,movimento)




