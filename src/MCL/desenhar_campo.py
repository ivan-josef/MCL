import numpy as np
import cv2 

_INTERSECOES = [
    {"tipo":"L","x":0,"y":0},
    {"tipo":"T","x":0,"y":0.5},
    {"tipo":"T","x":0,"y":1.5},
    {"tipo":"T","x":0,"y":4.5},
    {"tipo":"T","x":0,"y":5.5},
    {"tipo":"L","x":0,"y":6},
    {"tipo":"L","x":1,"y":1.5},
    {"tipo":"L","x":1,"y":4.5},
    {"tipo":"L","x":2,"y":0.5},
    {"tipo":"L","x":2,"y":5.5},
    {"tipo":"T","x":4.5,"y":0},
    {"tipo":"X","x":4.5,"y":2.25},
    {"tipo":"X","x":4.5,"y":3.75},
    {"tipo":"T","x":4.5,"y":6},
    {"tipo":"L","x":7,"y":0.5},
    {"tipo":"L","x":7,"y":5.5},
    {"tipo":"L","x":8,"y":1.5},
    {"tipo":"L","x":8,"y":4.5},
    {"tipo":"L","x":9,"y":0},
    {"tipo":"T","x":9,"y":0.5},
    {"tipo":"T","x":9,"y":1.5},
    {"tipo":"T","x":9,"y":4.5},
    {"tipo":"T","x":9,"y":5.5},
    {"tipo":"T","x":9,"y":6}
]

def converter_coord(x, y):

    px = int(x  * 100)

    py = int(y * 100) 
    
    return (px, py)


def desenhar_campo(particulas,pose_real):
                        #y  x
    np_map = np.full((600,900,3),(0,128,0),dtype=np.uint8)
    
    for i in _INTERSECOES:
        if i["tipo"] == "L":
            cv2.circle(np_map,(converter_coord(i['x'],i['y'])),10,(255,255,255),-1)
        if i["tipo"] == "T":
            cv2.circle(np_map,(converter_coord(i['x'],i['y'])),10,(0,0,0),-1)
        if i["tipo"] == "X":
            cv2.circle(np_map,(converter_coord(i['x'],i['y'])),10,(150,150,150),-1)

    for p in particulas:
        cv2.circle(np_map,(converter_coord(p['x'],p['y'])),5,(255,0,0),-1)


    # ground_thruth

    cv2.circle(np_map,(converter_coord(pose_real['x'],pose_real['y'])),5,(0,0,255),-1)

    cv2.imshow('teste',np_map)
    key = cv2.waitKey(0) & 0xFF
    return key


if __name__ == '__main__':
    desenhar_campo()