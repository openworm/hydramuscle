import numpy as np

def sig(v, vstar, sstar):
    "Sigmoidal function"
    return 1 / (1 + np.exp(-(v-vstar)/sstar))

def bell(v, vstar, sstar, taustar, tau0):
    "Bell-shape function"
    return taustar/(np.exp(-(v-vstar)/sstar) + np.exp((v-vstar)/sstar)) + tau0

def set_attr(obj, attr, val):
    "A wrapper of setattr(), raises error if attr not exists"
    if not hasattr(obj, attr):
        if not hasattr(obj, '_'+attr):
            raise AttributeError(obj.__class__.__name__ +
                                 " has no attribute " +
                                 attr)
        setattr(obj, '_'+attr, val)
    else:
        setattr(obj, attr, val)

def generate_indices(numy, xmin, xmax, ymin, ymax):
    "Generate indices from coordinates range"
    res = []

    for j in range(ymin, ymax):
        for i in range(xmin, xmax):
            res.append(i * numy + j)

    return res

def track_wavefront(data, thres):
    "Track the wavefront of trace data"

    ntime = len(data)
    numcell = len(data[0])

    wavefront = np.zeros(ntime)

    for j in range(ntime):
        for k in range(numcell-1, -1, -1):
            if data[j][k] > thres:
                wavefront[j] = k
                break

    return wavefront

def compress_frame(frame, size_x, size_y, to_size_x, to_size_y):
    "Compress the frame by averaging neighboring elements"
    mat = np.reshape(frame, (size_x, size_y))
    new_mat = np.zeros((to_size_x, to_size_y))
    win_x = int(size_x/to_size_x)
    win_y = int(size_y/to_size_y)

    for i in range(to_size_x):
        for j in range(to_size_y):
            new_mat[i, j] = np.mean(mat[i*win_x:(i+1)*win_x, j*win_y:(j+1)*win_y])

    return np.reshape(new_mat, (to_size_x*to_size_y))

def average_force(force, numx, numy):
    "Average the force to 20x20"

    force_averaged = np.zeros((len(force), 400))

    for j in range(len(force)):
        frame = force[j]

        force_averaged[j, :] = compress_frame(frame, numx, numy, 20, 20)

    return np.reshape(force_averaged, (-1, 20, 20))

def encode_force_2d(encoder, c, numx, numy, dt):
    "Encode calcium concentration matrix c into force"

    from hydramuscle.model.euler_odeint import euler_odeint

    c = c.reshape(-1, numx*numy)

    def _rhs(y, t, c, num2):
        "Right-hand side"

        j = int(t/dt)

        k1 = c[j]**encoder.nm / (c[j]**encoder.nm + encoder.c_half**encoder.nm)
        encoder.k6 = k1

        m, mp, amp, am = y[0:num2], y[num2:2*num2], y[2*num2:3*num2], y[3*num2:4*num2]

        dmdt = -k1*m + encoder.k2*mp + encoder.k7*am
        dmpdt = k1*m + (-encoder.k2 - encoder.k3)*mp + encoder.k4*amp
        dampdt = encoder.k3*mp + (-encoder.k4-encoder.k5)*amp + encoder.k6*am
        damdt = encoder.k5*amp + (-encoder.k6-encoder.k7)*am

        dydt = np.reshape([dmdt, dmpdt, dampdt, damdt], 4*num2)

        return dydt

    T = len(c) * dt

    num2 = numx * numy
    base_mat = np.ones((numy, numx))
    inits = [encoder.m0, encoder.mp0, encoder.amp0, encoder.am0]
    y0 = np.array([x*base_mat for x in inits])
    y0 = np.reshape(y0, 4*num2)
    
    sol = euler_odeint(rhs=_rhs,
                        y=y0,
                        T=T,
                        dt=dt,
                        save_interval=1,
                        c=c,
                        num2=num2)

    force = encoder.K * (sol[:, 2*num2:3*num2] + sol[:, 3*num2:4*num2])

    return force.reshape(-1, numx, numy)
    