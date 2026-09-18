import numpy as np
import cv2 
import simulador_fornecido as sim



def converter_coord(x, y):
    # O centro do campo (0,0) metros precisa virar o centro da imagem (300,200) pixels.
    # Multiplicamos por 100 para aplicar a escala (1 metro = 100 pixels).
    px = int((x + 3.0) * 100)
    
    # O eixo Y no OpenCV é invertido (o 0 começa no topo da tela e desce).
    # Por isso, subtraímos de 2.0 (que é o topo físico do campo) para consertar.
    py = int((2.0 - y) * 100) 
    
    return (px, py)


def desenhar_campo(particulas,pose_estimada,pose_real):
                        #y x
    np_map = np.zeros((400,600,3),dtype=np.uint8)

    cv2.circle(np_map,(converter_coord(0,0)),10,(255,255,255),-1)
    for i in sim._INTERSECOES:
        if i['tipo'] == 'L':
            cv2.circle(np_map,(converter_coord(i['x'],i['y'])),10,(255,255,255),-1)
        if i['tipo'] == 'T':
            cv2.circle(np_map,(converter_coord(i['x'],i['y'])),10,(150,150,150),-1)

    for p in particulas:
        cv2.circle(np_map,(converter_coord(p['x'],p['y'])),5,(255,0,0),-1)

    # pose estimada

    cv2.circle(np_map,(converter_coord(pose_estimada[0],pose_estimada[1])),5,(0,255,0),-1)

    # ground_thruth

    cv2.circle(np_map,(converter_coord(pose_real['x'],pose_real['y'])),5,(0,0,255),-1)



    cv2.imshow('teste',np_map)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    desenhar_campo()