"""E44 — noyau commun: GP amorti, vorticité, traceur de filaments, nombre de Gauss."""
import numpy as np, itertools, time

def gp_linear(N, A, gamma, dt):
    k = 2*np.pi*np.fft.fftfreq(N)
    k2 = k[:,None,None]**2 + k[None,:,None]**2 + k[None,None,:]**2
    return np.exp(-(1j+gamma)*A*k2*dt)

def gp_step(psi, lin, gamma, dt, fix=None):
    psi *= np.exp(-(1j+gamma)*(np.abs(psi)**2 - 1.0)*dt/2)
    psi = np.fft.ifftn(np.fft.fftn(psi)*lin)
    psi *= np.exp(-(1j+gamma)*(np.abs(psi)**2 - 1.0)*dt/2)
    if fix is not None:
        psi[fix[0]] = fix[1][fix[0]]
    return psi

def wrap(a): return (a+np.pi)%(2*np.pi)-np.pi

def vorticity(psi, amp_gate=0.1):
    th = np.angle(psi); am = np.abs(psi)
    def plaq(p00,p10,p11,p01):
        return np.rint((wrap(p10-p00)+wrap(p11-p10)+wrap(p01-p11)+wrap(p00-p01))/(2*np.pi)).astype(np.int8)
    def g4(a00,a10,a11,a01):
        return ((a00>amp_gate)&(a10>amp_gate)&(a11>amp_gate)&(a01>amp_gate))
    r = lambda x,ax: np.roll(x,-1,ax)
    wx = np.where(g4(am,r(am,1),r(r(am,1),2),r(am,2)), plaq(th,r(th,1),r(r(th,1),2),r(th,2)), 0)
    wy = np.where(g4(am,r(am,2),r(r(am,2),0),r(am,0)), plaq(th,r(th,2),r(r(th,2),0),r(th,0)), 0)
    wz = np.where(g4(am,r(am,0),r(r(am,0),1),r(am,1)), plaq(th,r(th,0),r(r(th,0),1),r(th,1)), 0)
    return wx, wy, wz

AXV = [np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1])]

def face_map(wx, wy, wz):
    F = {}
    for ax, w in enumerate((wx, wy, wz)):
        for idx in zip(*np.nonzero(w)):
            F[(ax,)+idx] = int(w[idx])
    return F

def cell_faces(c, N, F):
    ci,cj,ck = c[0]%N, c[1]%N, c[2]%N
    out = []
    cand = [((0,ci,cj,ck),-1), ((0,(ci+1)%N,cj,ck),+1),
            ((1,ci,cj,ck),-1), ((1,ci,(cj+1)%N,ck),+1),
            ((2,ci,cj,ck),-1), ((2,ci,cj,(ck+1)%N),+1)]
    for fk, osign in cand:
        w = F.get(fk)
        if w:
            s = 1 if w>0 else -1
            out.append((fk, osign*w, s))
    return out

def cell_center_rel(fk, c, N):
    ax,i,j,k = fk
    p = np.array([i, j+0.5, k+0.5]) if ax==0 else (np.array([i+0.5, j, k+0.5]) if ax==1 else np.array([i+0.5, j+0.5, k]))
    d = p - np.array([x%N for x in c]) - 0.5
    return (d + N/2) % N - N/2

def trace_filaments(wx, wy, wz):
    N = wx.shape[0]
    F = face_map(wx, wy, wz)
    pair_cache = {}
    anomalies = [0]; ambiguous = [0]
    def pairing(c):
        key = (c[0]%N, c[1]%N, c[2]%N)
        if key in pair_cache: return pair_cache[key]
        fl = cell_faces(c, N, F)
        ins  = [f for f in fl if f[1] < 0]
        outs = [f for f in fl if f[1] > 0]
        pm = {}
        if len(ins)==1 and len(outs)==1:
            pm[ins[0][0]] = (outs[0][0], outs[0][2])
        elif len(ins)==2 and len(outs)==2:
            ambiguous[0] += 1
            d_in  = [cell_center_rel(f[0], c, N) for f in ins]
            d_out = [cell_center_rel(f[0], c, N) for f in outs]
            best = None
            for perm in [(0,1),(1,0)]:
                sc = sum(abs(float(np.dot(d_in[a], d_out[b]))) for a,b in enumerate(perm))
                if best is None or sc > best[0]: best = (sc, perm)
            for a,b in enumerate(best[1]):
                pm[ins[a][0]] = (outs[b][0], outs[b][2])
        else:
            if fl: anomalies[0] += 1
        pair_cache[key] = pm
        return pm
    visited, filaments = set(), []
    for fk, w in F.items():
        s = 1 if w>0 else -1
        if (fk,s) in visited: continue
        c0 = np.array([fk[1],fk[2],fk[3]], dtype=int)
        c0[fk[0]] += 0 if s>0 else -1
        start = (fk, s); pts = []
        state, cell, cstart = start, c0.copy(), c0.copy()
        ok = True
        while True:
            visited.add(state)
            pm = pairing(cell)
            nxt = pm.get(state[0])
            if nxt is None: ok=False; break
            exit_fk, exit_s = nxt
            ax,i,j,k = exit_fk
            base = np.array([cell[0],cell[1],cell[2]])
            raw = np.array([i,j,k],dtype=float)
            adj = raw - (base % N)
            adj = (adj + N/2) % N - N/2
            cover = base + adj
            p_cov = cover + (np.array([0,0.5,0.5]) if ax==0 else (np.array([0.5,0,0.5]) if ax==1 else np.array([0.5,0.5,0])))
            pts.append(p_cov)
            cell = cell + exit_s*AXV[ax]
            state = (exit_fk, exit_s)
            if state == start: break
            if len(pts) > 100000: ok=False; break
        disp = cell - cstart
        filaments.append({'pts': np.array(pts), 'closed': ok and state==start,
                          'disp': disp, 'len': len(pts)})
    return filaments, anomalies[0], ambiguous[0]

def gauss_link_mi(P, Q, L):
    dP = np.roll(P,-1,axis=0)-P; dQ = np.roll(Q,-1,axis=0)-Q
    dP = (dP+L/2)%L-L/2;     dQ = (dQ+L/2)%L-L/2
    R  = P[:,None,:]-Q[None,:,:]
    R  = (R+L/2)%L-L/2
    cr = np.cross(dP[:,None,:], dQ[None,:,:])
    num = np.einsum('ijk,ijk->ij', R, cr)
    den = np.linalg.norm(R,axis=2)**3
    den[den<1e-9] = np.inf
    return float(np.sum(num/den)/(4*np.pi))

def analyse(psi, gate=0.1, min_len=6, max_loops=400):
    t0 = time.time()
    wx,wy,wz = vorticity(psi, amp_gate=gate)
    nfaces = int(np.sum(wx!=0)+np.sum(wy!=0)+np.sum(wz!=0))
    fils, anom, amb = trace_filaments(wx,wy,wz)
    loops = [f for f in fils if f['closed'] and not np.any(f['disp']) and f['len']>=min_len]
    opens = [f for f in fils if not (f['closed'] and not np.any(f['disp']))]
    loops.sort(key=lambda f: -f['len'])
    if len(loops) > max_loops: loops = loops[:max_loops]
    pairs = []
    for i,j in itertools.combinations(range(len(loops)),2):
        lk = gauss_link_mi(loops[i]['pts'], loops[j]['pts'], psi.shape[0])
        if abs(lk) >= 0.5: pairs.append((i,j,round(lk,3)))
    # amas liés: composantes connexes
    parent = list(range(len(loops)))
    def find(a):
        while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
        return a
    for i,j,_ in pairs:
        pi,pj = find(i),find(j)
        if pi!=pj: parent[pi]=pj
    clusters = {}
    for i,j,_ in pairs:
        r = find(i); clusters.setdefault(r,set()).update([i,j])
    mult = sorted(len(v) for v in clusters.values())
    res = {'nfaces': nfaces, 'nloops': len(loops), 'loop_lens': [int(f['len']) for f in loops],
           'nopens': len(opens), 'open_maxlen': max([f['len'] for f in opens], default=0),
           'anom': anom, 'amb': amb, 'pairs': pairs, 'cluster_mult': mult,
           'analyse_s': round(time.time()-t0,1)}
    return res, loops, pairs
