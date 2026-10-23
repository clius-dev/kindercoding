"""메인(B_0_main/main.html) BGM 1곡 — 'main-playroom-loop'.
generate_submain_bgm.py 와 같은 합성기(Song · 악기 · 리버브 · RMS 0.1041 정규화)를 쓴다.
놀이방 문을 여는 느낌: G 장조 · 138 BPM · 16마디 심리스 루프 · 마림바·글로켄 멜로디 + 8분 베이스 + 4온더플로어 킥·클랩 + 우쿨렐레 스트럼 (신나는 업템포).
사용: python generate_main_bgm.py <출력폴더>  → <name>.wav (후처리로 mp3)"""
import sys, wave
from pathlib import Path
import numpy as np

SR = 44_100
OUTDIR = Path(sys.argv[1])
NOTE = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def n(s):                       # 'F#4' -> midi
    m = NOTE[s[0]]; i = 1
    while s[i] in '#b':
        m += 1 if s[i]=='#' else -1; i += 1
    return m + 12*(int(s[i:])+1)
def fr(m): return 440.0 * 2 ** ((m - 69) / 12)

class Song:
    def __init__(self, name, bpm, bars=16, seed=1, swing=0.0):
        self.name, self.bpm, self.bars, self.swing = name, bpm, bars, swing
        self.beat = 60/bpm
        self.dur = bars*4*self.beat
        self.N = int(round(self.dur*SR))
        self.mix = np.zeros((self.N, 2))
        self.rng = np.random.default_rng(seed)
    def put(self, sig, beat, p=0.0, g=1.0):
        if self.swing and (beat*2) % 2 == 1:           # 오프비트 8분음표를 뒤로 (셔플)
            beat += self.swing
        s = int(round(beat*self.beat*SR))
        a = (np.clip(p,-1,1)+1)*np.pi/4
        st = np.column_stack((sig*np.cos(a), sig*np.sin(a)))*g
        idx = (np.arange(len(st))+s) % self.N
        np.add.at(self.mix, idx, st)
    def finish(self, reverb=((0.071,.13,0),(0.113,.10,1),(0.167,.07,0),(0.231,.05,1))):
        dry = self.mix.copy()
        for d,a,x in reverb:
            src = np.roll(dry, int(d*SR), axis=0)
            self.mix += (src[:, ::-1] if x else src)*a
        m = np.tanh(self.mix*0.9)
        # 아주 약한 로우패스 느낌(고음 쏘는 느낌 완화): 2-tap 평균
        m = 0.75*m + 0.25*np.roll(m, 1, axis=0)
        rms = float(np.sqrt((m**2).mean())); m *= 0.1041/rms
        pk = float(np.abs(m).max())
        assert pk < 0.97, (self.name, pk)
        pcm = (np.clip(m,-1,1)*32767).astype('<i2')
        out = OUTDIR/f'{self.name}.wav'
        with wave.open(str(out),'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
        print(self.name, 'dur %.2fs rms %.4f peak %.3f'%(self.dur, 0.1041, pk))

# ---------- 악기 ----------
def T(sec): return np.arange(int(sec*SR))/SR
def env(t, a, d): return (1-np.exp(-t/a))*np.exp(-t/d)
def marimba(m, sec):
    t=T(sec); f=fr(m)
    s=np.sin(2*np.pi*f*t)+.45*np.sin(2*np.pi*f*4*t)*np.exp(-t/.05)+.12*np.sin(2*np.pi*f*2*t)
    return s*env(t,.002,.22)
def pluck(m, sec, br=1.0):
    t=T(sec); f=fr(m)
    s=np.sin(2*np.pi*f*t)+.38*br*np.sin(2*np.pi*f*2*t)*np.exp(-t/.18)+.16*br*np.sin(2*np.pi*f*3*t)*np.exp(-t/.10)
    return s*env(t,.003,.27)
def musicbox(m, sec):
    t=T(sec); f=fr(m)
    s=np.sin(2*np.pi*f*t)+.35*np.sin(2*np.pi*f*3.01*t)*np.exp(-t/.10)+.15*np.sin(2*np.pi*f*5.02*t)*np.exp(-t/.05)
    return s*env(t,.002,.38)
def glock(m, sec):
    t=T(sec); f=fr(m)
    s=np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*2.76*t)*np.exp(-t/.14)
    return s*env(t,.002,.55)
def bass(m, sec, d=.20):
    t=T(sec); f=fr(m)
    return (np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*f*2*t))*env(t,.006,d)
def pizz(m, sec):
    t=T(sec); f=fr(m)
    return (np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*2*t)*np.exp(-t/.06))*env(t,.003,.13)
def stab(m, sec, d=.07):
    t=T(sec); f=fr(m)
    return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*2*t))*env(t,.004,d)
def pad(ms, sec):
    t=T(sec); s=np.zeros_like(t)
    for m in ms:
        f=fr(m)
        for det in (-.003,0,.003):
            s+=np.sin(2*np.pi*f*(1+det)*t)
    a=np.minimum(t/.35,1)*np.minimum((sec-t)/.5,1)
    return s*a/ (3*len(ms))
def kick(soft=1.0):
    t=T(.2); ph=2*np.pi*(45*t+75*(1-np.exp(-t/.035))*.035)
    return np.sin(ph)*np.exp(-t/.08)*soft
def noise_hp(sec, k):
    x=RNG.normal(0,1,int(sec*SR)); return x-np.convolve(x,np.ones(k)/k,mode='same')
RNG=np.random.default_rng(7)
def clap():
    t=T(.13); return noise_hp(.13,9)*np.exp(-t/.032)
def shaker(acc=False):
    t=T(.07); return noise_hp(.07,5)*np.exp(-t/.02)*(1.4 if acc else 1)
def wood(m=84):
    t=T(.06); return np.sin(2*np.pi*fr(m)*t)*np.exp(-t/.012)
def rim():
    t=T(.05); return (noise_hp(.05,7)*.5+np.sin(2*np.pi*1700*t))*np.exp(-t/.012)



def bars_loop16(song, prog, mel, per_bar):
    for bar in range(16):
        per_bar(song, bar//8, bar, bar*4, prog[bar], mel[bar])

def playroom():
    s=Song('main-playroom-loop',138,seed=93,swing=0.0)
    G =[n('G2'),n('B3'),n('D4'),n('G4')]; D =[n('D3'),n('A3'),n('D4'),n('F#4')]
    Em=[n('E2'),n('B3'),n('E4'),n('G4')]; C =[n('C3'),n('G3'),n('C4'),n('E4')]; Bm=[n('B2'),n('B3'),n('D4'),n('F#4')]
    prog=[G,D,Em,C, G,D,C,D,   C,D,Bm,Em, C,D,G,D]
    M=lambda *x:[(a,n(b),c) for a,b,c in x]
    mel=[M((0,'B4',1),(1,'D5',.5),(1.5,'G5',.5),(2,'B5',1),(3,'A5',1)),
         M((0,'A5',1),(1,'F#5',.5),(1.5,'A5',.5),(2,'D6',1),(3,'A5',1)),
         M((0,'G5',1),(1,'B5',.5),(1.5,'E6',.5),(2,'D6',1),(3,'B5',1)),
         M((0,'C6',1),(1,'G5',.5),(1.5,'E5',.5),(2,'G5',1),(3,'E5',1)),
         M((0,'B5',1),(1,'G5',.5),(1.5,'D5',.5),(2,'G5',1),(3,'B5',1)),
         M((0,'A5',1),(1,'D6',.5),(1.5,'C6',.5),(2,'A5',1),(3,'F#5',1)),
         M((0,'E5',1),(1,'G5',.5),(1.5,'C6',.5),(2,'B5',1),(3,'G5',1)),
         M((0,'A5',1),(1,'F#5',1),(2,'D5',1),(3,'A4',1)),
         M((0,'E6',1),(1,'D6',.5),(1.5,'C6',.5),(2,'B5',1),(3,'G5',1)),
         M((0,'F#5',1),(1,'A5',.5),(1.5,'D6',.5),(2,'C6',1),(3,'A5',1)),
         M((0,'D6',1),(1,'B5',.5),(1.5,'F#5',.5),(2,'B5',1),(3,'D6',1)),
         M((0,'E6',1),(1,'B5',.5),(1.5,'G5',.5),(2,'B5',1),(3,'E6',1)),
         M((0,'C6',1),(1,'E6',.5),(1.5,'G6',.5),(2,'E6',1),(3,'C6',1)),
         M((0,'A5',.5),(.5,'B5',.5),(1,'C6',1),(2,'D6',1),(3,'F#6',1)),
         M((0,'G6',1.5),(1.5,'F#6',.5),(2,'D6',1),(3,'B5',1)),
         M((0,'A5',1),(1,'B5',.5),(1.5,'A5',.5),(2,'F#5',1),(3,'A5',1))]
    def pb(s,rep,bar,b0,ch,m):
        s.put(pad(ch[1:],4*s.beat+.4),b0,0,.22)
        for at,mi,ln in m:
            if rep==0: s.put(marimba(mi,ln*s.beat+.25),b0+at,-.1,.34*s.rng.uniform(.96,1.04)); s.put(glock(mi+12,ln*s.beat+.3),b0+at,.2,.05)
            else:
                s.put(marimba(mi,ln*s.beat+.25),b0+at,-.12,.32*s.rng.uniform(.96,1.04))
                s.put(glock(mi+12,ln*s.beat+.4),b0+at,.25,.08)
        r=ch[0]
        for k in range(8):                                   # 8분음표 업비트 베이스(근음/5도 번갈아)
            s.put(bass(r+(7 if k%4 in (2,3) else 0),.5*s.beat+.05,.14),b0+k*.5,0,.30 if k%2==0 else .22)
        for k in range(8):                                   # 8분 스트럼 — 업비트 강조
            for i,mi in enumerate(ch[1:]): s.put(stab(mi,.18,.07),b0+k*.5+i*.015,-.3+.3*i,.075 if k%2 else .045)
        for k in range(4): s.put(kick(1.0),b0+k,0,.34)       # 4온더플로어 킥
        for at in (1,3): s.put(clap(),b0+at,-.1,.07)         # 2·4박 클랩
        for k in range(16): s.put(shaker(k%4==2),b0+k*.25,.3,.02 if k%2 else .012)   # 16분 하이햇
        if bar%4==3:                                         # 4마디마다 필인
            for j in range(4): s.put(wood(84+j*2),b0+3+j*.25,.2,.09)
        if rep==1 or bar in (4,5,6,7):                       # 후반/중반부터 멜로디 8분 아르페지오 반짝임
            for k,mi in enumerate(ch[1:]+ch[1:]): s.put(glock(mi+24,.4),b0+k*.5,.35,.05)
    bars_loop16(s,prog,mel,pb); s.finish()

playroom()
