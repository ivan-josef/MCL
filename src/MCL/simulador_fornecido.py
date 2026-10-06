"""Simulador fornecido para a atividade de filtro de partículas.

O módulo mantém uma pose real interna, simula os movimentos do robô e
produz observações com o mesmo formato esperado para uma câmera real.
Os alunos não devem usar a pose real no cálculo do filtro.
"""

from math import atan2, cos, hypot, pi, radians, sin
from random import Random
from typing import Optional

# Limites do campo didático, em metros.
X_MIN, X_MAX = -3.0, 3.0
Y_MIN, Y_MAX = -2.0, 2.0

# Interseções conhecidas pelo simulador.
_INTERSECOES = [
    {"tipo": "L", "x": -3.0, "y": -2.0},
    {"tipo": "L", "x": -3.0, "y": 2.0},
    {"tipo": "L", "x": 3.0, "y": -2.0},
    {"tipo": "L", "x": 3.0, "y": 2.0},
    {"tipo": "L", "x": -2.0, "y": -1.0},
    {"tipo": "L", "x": -2.0, "y": 1.0},
    {"tipo": "L", "x": 2.0, "y": -1.0},
    {"tipo": "L", "x": 2.0, "y": 1.0},
    {"tipo": "T", "x": 0.0, "y": -2.0},
    {"tipo": "T", "x": 0.0, "y": 2.0},
    {"tipo": "T", "x": -3.0, "y": -1.0},
    {"tipo": "T", "x": -3.0, "y": 1.0},
    {"tipo": "T", "x": 3.0, "y": -1.0},
    {"tipo": "T", "x": 3.0, "y": 1.0},
]

# Configuração da câmera simulada.
ALCANCE_MAXIMO_M = 3.0
MEIO_CAMPO_VISAO_RAD = radians(35.0)  # Campo de visão total: 70 graus.
DESVIO_DISTANCIA_M = 0.03
DESVIO_ANGULO_RAD = radians(2.0)
PROBABILIDADE_FALHA = 0.05

# Ruído do movimento real simulado.
DESVIO_AVANCO_M = 0.02
DESVIO_GIRO_RAD = radians(1.5)

# Sequência sugerida para os primeiros testes.
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

_pose_real = {"x": -1.0, "y": -1.0, "theta": radians(-20.0)}
_rng_movimento = Random(7)
_rng_camera = Random(8)


def _normalizar_angulo(angulo_rad: float) -> float:
    """Normaliza um ângulo para o intervalo [-pi, pi]."""
    while angulo_rad > pi:
        angulo_rad -= 2.0 * pi
    while angulo_rad < -pi:
        angulo_rad += 2.0 * pi
    return angulo_rad


def _esta_dentro_do_campo(x: float, y: float) -> bool:
    return X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX


def reiniciar_simulacao(semente: int = 7) -> None:
    """Reinicia a pose real e os geradores aleatórios.

    A mesma semente produz o mesmo experimento, facilitando a comparação
    entre implementações diferentes do filtro.
    """
    global _pose_real, _rng_movimento, _rng_camera

    _pose_real = {
        "x": -1.0,
        "y": -1.0,
        "theta": radians(-20.0),
    }
    _rng_movimento = Random(semente)
    _rng_camera = Random(semente + 1)


def executar_movimento(comando: str, valor: float) -> bool:
    """Aplica um comando à pose real simulada.

    Parâmetros:
        comando: "avancar" ou "girar".
        valor: metros para avanço; radianos para giro.

    Retorna True quando o movimento foi aplicado. Um avanço que levaria
    o robô para fora do campo é rejeitado e retorna False.
    """
    comando = comando.strip().lower()

    if comando == "avancar":
        deslocamento = max(
            0.0,
            valor + _rng_movimento.gauss(0.0, DESVIO_AVANCO_M),
        )
        novo_x = _pose_real["x"] + deslocamento * cos(_pose_real["theta"])
        novo_y = _pose_real["y"] + deslocamento * sin(_pose_real["theta"])

        if not _esta_dentro_do_campo(novo_x, novo_y):
            return False

        _pose_real["x"] = novo_x
        _pose_real["y"] = novo_y
        return True

    if comando == "girar":
        giro = valor + _rng_movimento.gauss(0.0, DESVIO_GIRO_RAD)
        _pose_real["theta"] = _normalizar_angulo(
            _pose_real["theta"] + giro
        )
        return True

    raise ValueError('comando deve ser "avancar" ou "girar"')


def obter_observacao_camera() -> Optional[dict]:
    """Retorna a interseção visível mais próxima.

    Formato do retorno:
        {
            "tipo": "L" ou "T",
            "distancia_m": float positivo,
            "angulo_rad": float entre -pi e pi,
        }

    Convenção angular:
        positivo = esquerda; negativo = direita.

    Retorna None quando nenhuma interseção estiver no alcance e no campo
    de visão, ou quando ocorrer uma falha simulada de detecção.
    """
    if _rng_camera.random() < PROBABILIDADE_FALHA:
        return None

    visiveis = []

    for intersecao in _INTERSECOES:
        dx = intersecao["x"] - _pose_real["x"]
        dy = intersecao["y"] - _pose_real["y"]
        distancia = hypot(dx, dy)
        angulo_global = atan2(dy, dx)
        angulo_relativo = _normalizar_angulo(
            angulo_global - _pose_real["theta"]
        )

        if distancia > ALCANCE_MAXIMO_M:
            continue
        if abs(angulo_relativo) > MEIO_CAMPO_VISAO_RAD:
            continue

        visiveis.append(
            {
                "tipo": intersecao["tipo"],
                "distancia_m": distancia,
                "angulo_rad": angulo_relativo,
            }
        )

    if not visiveis:
        return None

    observacao = min(visiveis, key=lambda item: item["distancia_m"])

    distancia_com_ruido = max(
        0.01,
        observacao["distancia_m"]
        + _rng_camera.gauss(0.0, DESVIO_DISTANCIA_M),
    )
    angulo_com_ruido = _normalizar_angulo(
        observacao["angulo_rad"]
        + _rng_camera.gauss(0.0, DESVIO_ANGULO_RAD)
    )

    return {
        "tipo": observacao["tipo"],
        "distancia_m": distancia_com_ruido,
        "angulo_rad": angulo_com_ruido,
    }


def obter_pose_real_para_validacao() -> dict:
    """Retorna uma cópia da pose real apenas para gráficos e avaliação.

    Esta função não pode ser usada para calcular pesos ou corrigir as
    partículas, pois isso eliminaria o problema de localização.
    """
    return dict(_pose_real)
