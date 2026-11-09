import json, subprocess, sys, numpy as np
from PIL import Image
FPS=30; OUT=sys.argv[1]
B=json.load(open('bands.json'))
imgs=[np.asarray(Image.open(f'src/k{i}.png').convert('RGB'),dtype=np.float32)[:1232] for i in (1,2,3)]
bands=[B[f'k{i}'] for i in (1,2,3)]
H,W,_=imgs[0].shape
PUSH,WHOLE,MOVE,HOLD,STAG=1.0,0.4,1.1,0.5,0.08
START=PUSH+WHOLE+MOVE  # open on the first picture already striped, = the still it replaces
SLIDE=PUSH+WHOLE+MOVE+HOLD
def ease(t):
    t=np.clip(t,0,1); return np.where(t<.5,4*t**3,1-(-2*t+2)**3/2)
X=np.arange(W,dtype=np.float32)
def gather(img,src):
    i0=np.floor(src).astype(int); f=(src-i0)[None,:,None]
    return img[:,i0%W]*(1-f)+img[:,(i0+1)%W]*f
def order(k,j,n):  # which band starts first: right->left, left->right, centre->out
    if k==0: return n-1-j
    if k==1: return j
    c=(n-1)/2; return abs(j-c)
def state(k,t):
    rb=bands[k]; n=len(rb); shift=np.zeros(W,np.float32)
    last=max(order(k,j,n) for j in range(n)); span=MOVE-STAG*last
    for j,(x0,x1,_,o) in enumerate(rb):
        shift[x0:x1]=-o*float(ease((t-STAG*order(k,j,n))/span))
    return gather(imgs[k],X-shift)
N=int(round(SLIDE*3*FPS))
ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
    '-vf','scale=1522:924:flags=lanczos','-an','-c:v','libx264','-crf','24','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for n in range(N):
    T=(n/FPS+START)%(SLIDE*3); k=int(T//SLIDE)%3; t=T-k*SLIDE
    if t<PUSH:
        cut=int(round(float(ease(t/PUSH))*W))
        old=state((k-1)%3,99); frame=np.empty_like(old)
        frame[:,cut:]=old[:,:W-cut]; frame[:,:cut]=imgs[k][:,W-cut:]
    elif t<PUSH+WHOLE: frame=imgs[k]
    else: frame=state(k,t-PUSH-WHOLE)
    ff.stdin.write(np.clip(frame,0,255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait(); print('secs',SLIDE*3)
