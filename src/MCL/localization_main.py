from . import simulador_fornecido as sim
from . import particle_filter as pf
from .desenhar_campo import desenhar_campo
import cv2 




def executar_filtro():
    
    particulas = pf.criar_particulas(200)

    while True:
    
        mov = sim.obter_proximo_movimento()
        if not mov:
            break

        pf.mover_particulas(particulas,mov)

        obs = simulador_fornecido.obter_observacao_camera()
        if obs:

            particle_filter.calcular_pesos(obs,particulas)


            particle_filter.normalizar_pesos(particulas)

            particulas = particle_filter.reamostragem(particulas)

        pose = particle_filter.estimar_pose(particulas)

        key = desenhar_campo(particulas,simulador_fornecido.obter_pose_real_para_validacao())

        if key == ord('q'):
            return
        if key == ord('r'):
            simulador_fornecido.reiniciar_simulacao()
            particulas = particle_filter.criar_particulas(200)


cv2.destroyAllWindows()



if __name__ == '__main__':
    executar_filtro()
