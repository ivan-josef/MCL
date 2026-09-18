import particle_filter
from desenhar_campo import desenhar_campo
import simulador_fornecido
import cv2 




def executar_filtro():
    particulas = particle_filter.criar_particulas(200)

    while True:

        for i in simulador_fornecido.COMANDOS_TESTE:
            mov = simulador_fornecido.executar_movimento(i[0],i[1])
            if mov:
                particle_filter.mover_particulas(particulas,i[0])

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
