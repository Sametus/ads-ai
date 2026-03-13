import numpy as np

def calculate_new_loc():
    theta = np.random.uniform(0, 2*np.pi)
    px = 300 * np.cos(theta)
    pz = 300 * np.sin(theta)
    ry = 180.0
    rz = 90.0 - np.degrees(np.arctan2(pz,px))
    return px,pz,ry,rz

px,pz,ry,rz = calculate_new_loc()

print("*"*10)
print("POS:")
print("pos x: ", px)
print("pos z: ", pz)
print("*"*10)
print("ROT:")
print("rot y: ", ry)
print("rot z: ", rz)
print("*"*10)
print("-"*10)