"""Fonte de dados de teste para o MCL, sem ROS 2 e sem estado de robô.

obter_proximo_movimento() entrega um comando por chamada e retorna None ao fim.
Não executa movimentos, não calcula uma trajetória e não mantém pose de robô.
O filtro é responsável por propagar as partículas a partir dos dados recebidos.

obter_observacao(numero) entrega uma mensagem de visão fictícia associada ao
número do movimento. A associação é apenas uma convenção do teste: as caixas
em pixels NÃO são calculadas a partir dos comandos, de uma pose ou de um campo.
Use esses exemplos para testar a leitura da mensagem. Eles não permitem validar
convergência ou precisão da localização; para isso, use dados de uma sequência
coerente de comandos e observações, por exemplo uma gravação do robô.

obter_observacao_mcl(numero) entrega uma lista para testar a entrada do MCL:
    [{'classe': 'l_intersection', 'distance_m': 2.0, 'angle_rad': 0.2}, ...]
Cada item corresponde a uma detecção presente na visão fictícia. 'classe' é o
tipo do objeto, não a identidade de um ponto único do campo. distance_m é a
distância horizontal em metros; angle_rad é o azimute relativo à frente do
robô, em radianos: zero à frente, positivo à esquerda e negativo à direita.
Adota-se o referencial base_footprint, com x para frente e y para a esquerda.
Os ângulos são FICTÍCIOS, conforme solicitado. As distâncias também são valores
de teste, enquanto não houver uma saída real do SoccerIPM. As faixas abaixo
são configuráveis, não representam alcance/FOV nem incertezas calibradas.
Nenhum desses valores é inferido das caixas em pixels ou dos movimentos.
Não há amostragem de ruído das partículas neste módulo.

Integração futura com SoccerIPM:
    https://ipm-docs.readthedocs.io/en/latest/soccer.html#socceripm
O pacote projeta detecções 2D para posições 3D usando CameraInfo e TF. É preciso
adaptar VisionData para soccer_vision_2d_msgs e fornecer a calibração/TF reais.
Sua saída usa soccer_vision_3d_msgs. Este arquivo não executa o pacote e a lista
do MCL acima é um formato interno de teste, não uma mensagem ROS do SoccerIPM.
Para um ponto já projetado no referencial do robô, distancia_plana_ipm(x_m, y_m)
calcula a distância no plano com hypot(x_m, y_m). Não passe pixels a ela.
Quando essa integração existir, atan2(y_m, x_m) também permitirá calcular o
azimute para um ponto diferente da origem. Por enquanto, o ângulo é sorteado.

Retorno:
    {
        'numero': 1,
        'comando': {
            'linear':  {'x': 0.04, 'y': 0.0, 'z': 0.0},  # m/s
            'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0},   # rad/s
        },
        'dt': 1.2,  # segundos de aplicação desse comando no teste
    }

'comando' reproduz os campos de geometry_msgs/msg/Twist usados em /cmd_vel.
'numero' e 'dt' são metadados do teste; NÃO fazem parte da mensagem Twist.
No ROS 2 real, o intervalo da predição deve vir do relógio/ciclo do filtro.

Visão: os dicionários reproduzem os campos de edrom_msgs/msg/VisionData,
Detection e DetectionArray do edrom_main.zip enviado pela equipe. O lançamento
principal usa object_finder, que publica em 'vision2BhvTopic':
    searching: bool; fps: int (uint8 no ROS)
    ball, robot, leftgoal, rightgoal: Detection
    x_intersection, l_intersection, t_intersection, center: DetectionArray
    Detection = {found, x, y, roi_width, roi_height}
    DetectionArray = {found, detections: [Detection, ...]}

x e y são o CENTRO da caixa na imagem, em pixels; roi_width e roi_height são
suas dimensões, também em pixels. A classe é indicada pelo campo da mensagem.
Esse tópico não publica distância, ângulo, confiança, ID de landmark ou header.
Os exemplos usam imagem 640x480 e fps=30 apenas como parâmetros de teste; isso
não determina a resolução/frequência real e não agenda chamadas em tempo real.
Geram-se bola, gols e interseções L/T/X. robot e center ficam ausentes, mantendo
os campos da mensagem. A cada cinco exemplos, o frame não contém detecções.
Uma Detection ausente tem found=False e números zero; um DetectionArray ausente
tem found=False e detections=[]. Não se pode inferir posição no campo desses
pixels sem um modelo geométrico de observação e a calibração correspondente.

Há também LandmarkArray em 'vision/landmarks' no repositório, com distance_m e
angle_rad, mas o publicador encontrado é localization_pkg/Simulation.py.
Esses valores não são a saída do object_finder usado no lançamento principal.

Faixas de TESTE: |vx| <= 0.05 m/s, |vy| <= 0.03 m/s, |wz| <= 0.15 rad/s.
Um único eixo é solicitado por comando; não se somam máximos em vários eixos.
São valores escolhidos abaixo dos comandos de teleoperação encontrados em
aurea_driver.py (0.1 m/s e 0.21 rad/s). Esses valores de teleoperação NÃO são
limites físicos certificados. Confirmar os limites reais com a equipe.
Não há validação de torque, aceleração, equilíbrio, limites articulares ou ZMP.

Uso:
    reiniciar_sequencia(seed=42)
    while True:
        dado = obter_proximo_movimento()
        if dado is None:
            break
        comando = dado['comando']
        dt = dado['dt']
        observacao = obter_observacao(dado['numero'])
        observacoes_mcl = obter_observacao_mcl(dado['numero'])
        # Passe comando e dt à SUA função de predição, uma vez por dado.
        # observacao: mensagem de visão em pixels.
        # observacoes_mcl: classes, distâncias e ângulos fictícios para o MCL.

As 20 mensagens são sorteadas ao reiniciar a sequência. A mesma seed permite
repetir exatamente o teste. Mude a seed para obter outra sequência.
"""

from copy import deepcopy
from math import hypot, isfinite, pi
import random

QUANTIDADE_MOVIMENTOS = 20
FAIXAS_TESTE = {
    'vx': (0.02, 0.05),   # módulo da velocidade para frente/trás, m/s
    'vy': (0.015, 0.03),  # módulo da velocidade lateral, m/s
    'wz': (0.05, 0.15),   # módulo da velocidade de giro, rad/s
}
DURACOES_S = (0.6, 1.2, 1.8)
RESOLUCAO_TESTE = (640, 480)  # largura, altura em pixels; não é calibração real
FPS_TESTE = 30
FAIXA_DISTANCIA_TESTE_M = (0.3, 4.0)
FAIXA_ANGULO_TESTE_RAD = (-pi / 3, pi / 3)  # -60 a +60 graus, arbitrários


def _deteccao_vazia():
    return {'found': False, 'x': 0, 'y': 0, 'roi_width': 0, 'roi_height': 0}


def _deteccao_teste(rng, gol=False):
    """Caixa fictícia contida na imagem; não estima distância ou orientação."""
    largura, altura = RESOLUCAO_TESTE
    w = rng.randrange(12, 50, 2)
    h = rng.randrange(60, 180, 2) if gol else rng.randrange(12, 50, 2)
    return {
        'found': True,
        'x': rng.randint(w // 2, largura - 1 - w // 2),
        'y': rng.randint(h // 2, altura - 1 - h // 2),
        'roi_width': w,
        'roi_height': h,
    }


def _observacao_teste(rng, numero):
    """Reproduz a estrutura publicada de VisionData, com valores artificiais."""
    obs = {'searching': True, 'fps': FPS_TESTE}
    for campo in ('ball', 'robot', 'leftgoal', 'rightgoal'):
        obs[campo] = _deteccao_vazia()
    for campo in ('x_intersection', 'l_intersection', 't_intersection', 'center'):
        obs[campo] = {'found': False, 'detections': []}
    if numero % 5 == 0:
        return obs
    for campo in ('ball', 'leftgoal', 'rightgoal'):
        if rng.random() < 0.6:
            obs[campo] = _deteccao_teste(rng, gol=(campo != 'ball'))
    for campo in ('x_intersection', 'l_intersection', 't_intersection'):
        deteccoes = [_deteccao_teste(rng) for _ in range(rng.randrange(3))]
        obs[campo] = {'found': bool(deteccoes), 'detections': deteccoes}
    return obs


def _observacao_mcl_teste(obs, rng):
    """Uma medida fictícia por detecção encontrada; [] quando não há detecção."""
    medidas = []
    for classe in ('ball', 'leftgoal', 'rightgoal',
                   'l_intersection', 't_intersection', 'x_intersection'):
        grupo = obs[classe]
        if not grupo['found']:
            continue
        deteccoes = grupo.get('detections', [grupo])
        for deteccao in deteccoes:
            if deteccao['found']:
                medidas.append({
                    'classe': classe,
                    'distance_m': rng.uniform(*FAIXA_DISTANCIA_TESTE_M),
                    'angle_rad': rng.uniform(*FAIXA_ANGULO_TESTE_RAD),
                })
    return medidas


def distancia_plana_ipm(x_m, y_m):
    """Distância horizontal de um ponto IPM já expresso no frame do robô.

    x_m e y_m devem estar em metros, relativos à origem de base_footprint.
    Não calcula a projeção IPM, não usa z e não recebe coordenadas de pixels.
    """
    x_m, y_m = float(x_m), float(y_m)
    if not isfinite(x_m) or not isfinite(y_m):
        raise ValueError('As coordenadas IPM devem ser finitas, em metros.')
    distancia = hypot(x_m, y_m)
    if not isfinite(distancia):
        raise ValueError('A distância IPM não é finita.')
    return distancia


def reiniciar_sequencia(seed=42):
    """Sorteia 20 comandos e 20 observações de teste; reinicia a leitura."""
    global _movimentos, _observacoes, _observacoes_mcl, _proximo
    rng = random.Random(seed)
    _movimentos, _proximo = [], 0
    for numero in range(1, QUANTIDADE_MOVIMENTOS + 1):
        eixo = rng.choice(('vx', 'vy', 'wz'))
        minimo, maximo = FAIXAS_TESTE[eixo]
        velocidade = rng.choice((-1, 1)) * round(rng.uniform(minimo, maximo), 4)
        comando = {
            'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        }
        if eixo == 'vx':
            comando['linear']['x'] = velocidade
        elif eixo == 'vy':
            comando['linear']['y'] = velocidade
        else:
            comando['angular']['z'] = velocidade
        _movimentos.append({'numero': numero, 'comando': comando,
                            'dt': rng.choice(DURACOES_S)})
    # Fluxo aleatório separado para preservar os movimentos da versão anterior.
    rng_visao = random.Random(seed)
    _observacoes = [
        _observacao_teste(rng_visao, numero)
        for numero in range(1, QUANTIDADE_MOVIMENTOS + 1)
    ]
    rng_mcl = random.Random(seed)
    _observacoes_mcl = [_observacao_mcl_teste(obs, rng_mcl) for obs in _observacoes]


def obter_proximo_movimento():
    """Entrega cópia do próximo dado. Após o vigésimo, retorna None."""
    global _proximo
    if _proximo >= len(_movimentos):
        return None
    dado = deepcopy(_movimentos[_proximo])
    _proximo += 1
    return dado


def obter_todos_movimentos():
    """Permite consultar a sequência inteira sem avançar a leitura."""
    return deepcopy(_movimentos)


def obter_observacao(numero):
    """Cópia de VisionData para um número de 1 a 20; não avança a sequência.

    Exemplo: obter_observacao(dado['numero']). O retorno contém somente os
    campos da mensagem de visão. Chamadas repetidas devolvem o mesmo conteúdo.
    """
    if type(numero) is not int or not 1 <= numero <= QUANTIDADE_MOVIMENTOS:
        raise ValueError('numero deve ser um inteiro de 1 a 20')
    return deepcopy(_observacoes[numero - 1])


def obter_observacao_mcl(numero):
    """Lista de {classe, distance_m, angle_rad} fictícios para a etapa 1 a 20.

    Distância no plano em metros e ângulo em radianos relativos a base_footprint.
    Valores fixos para a mesma sequência/seed; não sorteia ruído por partícula.
    Retorna [] sem detecções e uma cópia dos dados nas demais etapas.
    """
    if type(numero) is not int or not 1 <= numero <= QUANTIDADE_MOVIMENTOS:
        raise ValueError('numero deve ser um inteiro de 1 a 20')
    return deepcopy(_observacoes_mcl[numero - 1])


reiniciar_sequencia()

if __name__ == '__main__':
    import json
    while True:
        dado = obter_proximo_movimento()
        if dado is None:
            break
        print(json.dumps({
            **dado,
            'observacao': obter_observacao(dado['numero']),
            'observacoes_mcl': obter_observacao_mcl(dado['numero']),
        }))
