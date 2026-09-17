import random 
import math
import simulador_fornecido


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

def normalizar_angulo(angulo):
    pi = math.pi

    while angulo > pi:
        angulo -= 2.0 * pi
    while angulo < -pi:
        angulo += 2.0 * pi
    return angulo
     

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
        particula['theta'] = normalizar_angulo(particula['theta'])

        

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
                particula['x'] = pos_old['x']
                particula['y'] = pos_old['y']
                break

def mover_particulas(particulas,movimento):

    for p in particulas:
        aplicar_movimento(p,movimento)


# atualização: aplicação do modelo de observação


def calcular_distancia(obs,particula):
    obs_particula = []
    for i in simulador_fornecido._INTERSECOES:
        if i['tipo'] == obs['tipo']:
            xi = i['x']
            yi = i['y']
            xp = particula['x']
            yp = particula['y']
            euclid = math.sqrt((xi-xp)**2 + (yi-yp)**2)
            ang_glob = math.atan2(yi-yp,xi-xp)
            obs_particula.append({
                'tipo':i['tipo'],
                'distancia':euclid,
                'angulo_rel_rad':normalizar_angulo(ang_glob-particula['theta']) # representa onde a particula acha que a interseção deveria estar
            })
    return obs_particula


def calcular_peso_particula(obs,particula):
    obs_particula = calcular_distancia(obs,particula)
    if obs_particula == []:
        particula['w'] = 0.1
    else:
        pesos = []
        for p in obs_particula:
            erro_dist = abs(p['distancia'] - obs['distancia_m'])
            erro_ang = abs(normalizar_angulo(p['angulo_rel_rad'] - obs['angulo_rad']))
            if erro_dist <= 0.2 and erro_ang <= math.radians(5):
                pesos.append(10)
            elif erro_dist <= 0.5 and erro_ang <= math.radians(15):
                pesos.append(5)
            elif erro_dist <= 1 and erro_ang <= math.radians(30):
                pesos.append(2)
            else:
                pesos.append(0.2)

        particula['w'] = max(pesos)

def calcular_pesos(obs,particulas):
    for p in particulas:
        calcular_peso_particula(obs,p)

def normalizar_pesos(particulas):
    pesos_sum = 0
    for p in particulas:
        pesos_sum += p['w'] 
    for p in particulas:
        p['w'] = p['w']/pesos_sum


# Reamostragem

def reamostragem(particulas_old):
    pesos = []
    particulas_new = []
    for particula in particulas_old:
        pesos.append(particula['w'])
    particulas_reamostradas = random.choices(particulas_old,pesos,k=len(particulas_old))
    for p in particulas_reamostradas:
        particulas_new.append({
            'x':p['x'],
            'y':p['y'],
            'theta':p['theta'],
            'w': 1 / len(particulas_old),
        })

    return particulas_new

# estimação da posição do robo

def estimar_pose(particulas):
    x = 0
    y = 0
    sen_theta = []
    cos_theta = []
    for p in particulas:
        x += p['x']
        y += p['y']
        sen_theta.append(math.sin(p['theta']))
        cos_theta.append(math.cos(p['theta']))

    mean_x = x / len(particulas)
    mean_y = y / len(particulas)
    theta_estimado = math.atan2(sum(sen_theta)/len(sen_theta),sum(cos_theta)/len(cos_theta))
    pose = (mean_x,mean_y,theta_estimado)

    return pose 

    
        

if __name__ == '__main__':
    particulas = criar_particulas(50)
    for p in particulas:
        print(p)

    mover_particulas(particulas,'avancar')
    mover_particulas(particulas,'girar')
    print('--------------------')
    for p in particulas:
            print(p)

    obs = simulador_fornecido.obter_observacao_camera() # o angulo_rad do simulador representa onde a camera do robo realmente viu a interseção
    print('observação da camera',obs)
    calcular_pesos(obs,particulas)
    normalizar_pesos(particulas)

    print('--------------------')
    for p in particulas:
            print(p)
    print('--------------------')
    particulas = reamostragem(particulas)
    for p in particulas:
            print(p)

    print('--------------------')
    pose = estimar_pose(particulas)
    print('pose',pose)
        




    



