import math
import random
from math import cos, sin

# inicialização: ageração das particulas

def criar_particulas(n_particulas):

    particulas = [{'x':random.uniform(0,9),'y':random.uniform(0,6),'theta':random.uniform(-math.pi,math.pi),'w': 1/n_particulas} for x in range(n_particulas)]

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
    
    vx = movimento['comando']['linear']['x']
    vy = movimento['comando']['linear']['y']
    vz = movimento['comando']['angular']['z'] # rad/s
    dt = movimento['dt']

    theta = particula['theta'] # orientação antes do movimento ser realizado    

    incerteza_x = 0
    incerteza_y = 0
    incerteza_z = 0

    dx = (vx * dt + random.uniform(-incerteza_x,incerteza_x)) * 100
    dy = (vy * dt + random.uniform(-incerteza_y,incerteza_y)) * 100
    dz = vz * dt + random.uniform(-incerteza_z,incerteza_z)
    
    particula["x"] += (dx * cos(theta) - dy * sin(theta)) 
    particula["y"] += (dx * sin(theta) + dy * cos(theta)) 
    particula["theta"] = normalizar_angulo(theta + dz ) 

def mover_particulas(particulas,movimento):

    for p in particulas:
        aplicar_movimento(p,movimento)


# atualização: aplicação do modelo de observação


def calcular_distancia(obs,numero,particula,intersecoes):
    obs_particula = []
    for i in intersecoes:
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
    


