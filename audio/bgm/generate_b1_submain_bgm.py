"""서브메인(B-1_00.submain) 숲속 어린이집 등원길 BGM — 'submain-forest-kindergarten-loop'.
generate_puzzle_bgm.py 와 같은 합성기(Song · 악기 · 리버브 · RMS 0.1041 정규화)를 쓴다.
숲속 등원길: G 장조 · 108 BPM · 16마디 심리스 루프 · 마림바 멜로디 + 우쿨렐레 스트럼 + 약한 패드 + 어린이집 종(글록) + 새소리.
사용: python generate_submain_bgm.py <출력폴더>  → <name>.wav (후처리로 mp3)"""
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


# ---------- 봄 새소리 (4마디·12마디 끝에 짧게) ----------
def chirp(f0, f1, sec=.11):
    t=T(sec); f=f0+(f1-f0)*(t/sec)**.7
    ph=2*np.pi*np.cumsum(f)/SR + .6*np.sin(2*np.pi*28*t)
    return np.sin(ph)*np.exp(-((t-sec*.45)/(sec*.32))**2)

def bars_loop16(song, prog, mel, per_bar):          # 16마디를 그대로 (A 8마디 + B 8마디)
    for bar in range(16):
        per_bar(song, bar//8, bar, bar*4, prog[bar], mel[bar])

def forest():
    s=Song('submain-forest-kindergarten-loop',108,seed=81,swing=0.06)
    G =[n('G2'),n('G3'),n('B3'),n('D4')]; D =[n('D3'),n('A3'),n('D4'),n('F#4')]
    Em=[n('E2'),n('G3'),n('B3'),n('E4')]; C =[n('C3'),n('G3'),n('C4'),n('E4')]
    Bm=[n('B2'),n('F#3'),n('B3'),n('D4')]; Am=[n('A2'),n('E3'),n('A3'),n('C4')]
    prog=[G,D,Em,C, G,D,C,D,   Em,Bm,C,G, Am,D,G,D]
    M=lambda *x:[(a,n(b),c) for a,b,c in x]
    mel=[M((0,'B4',.5),(.5,'D5',.5),(1,'G5',1),(2,'F#5',.5),(2.5,'E5',.5),(3,'D5',1)),
         M((0,'A4',.5),(.5,'D5',.5),(1,'F#5',1),(2,'E5',1),(3,'D5',1)),
         M((0,'G5',1),(1,'E5',.5),(1.5,'G5',.5),(2,'B5',1),(3,'G5',1)),
         M((0,'E5',1),(1,'G5',.5),(1.5,'E5',.5),(2,'C5',1),(3,'D5',1)),
         M((0,'B4',.5),(.5,'D5',.5),(1,'G5',1),(2,'A5',.5),(2.5,'G5',.5),(3,'D5',1)),
         M((0,'F#5',1),(1,'A5',.5),(1.5,'F#5',.5),(2,'D5',1),(3,'A4',1)),
         M((0,'E5',1),(1,'G5',.5),(1.5,'C6',.5),(2,'B5',1),(3,'G5',1)),
         M((0,'A5',1),(1,'F#5',.5),(1.5,'D5',.5),(2,'F#5',1),(3,'A5',1)),
         M((0,'G5',1),(1,'B5',.5),(1.5,'G5',.5),(2,'E5',1),(3,'G5',1)),
         M((0,'F#5',.5),(.5,'B5',.5),(1,'D6',1),(2,'B5',1),(3,'F#5',1)),
         M((0,'E5',1),(1,'G5',.5),(1.5,'C6',.5),(2,'E6',1),(3,'C6',1)),
         M((0,'B5',1),(1,'G5',.5),(1.5,'D5',.5),(2,'G5',1),(3,'B5',1)),
         M((0,'C6',1),(1,'A5',.5),(1.5,'E5',.5),(2,'A5',1),(3,'C6',1)),
         M((0,'A5',.5),(.5,'B5',.5),(1,'C6',1),(2,'F#5',1),(3,'A5',1)),
         M((0,'D6',1.5),(1.5,'B5',.5),(2,'G5',1),(3,'D5',1)),
         M((0,'A4',1),(1,'B4',.5),(1.5,'A4',.5),(2,'F#4',1),(3,'A4',1))]
    def pb(s,rep,bar,b0,ch,m):
        s.put(pad(ch[1:],4*s.beat+.4),b0,0,.22)
        for at,mi,ln in m:
            s.put(marimba(mi,ln*s.beat+.25),b0+at,-.12,.33*s.rng.uniform(.96,1.04))
            if rep==1: s.put(glock(mi+12,ln*s.beat+.4),b0+at,.25,.08)
        r=ch[0]
        for at,off,ln in ((0,0,.7),(2,7,.55)):
            s.put(bass(r+off,ln*s.beat+.1,.22),b0+at,0,.34)
        for at in (1,3):
            for i,mi in enumerate(ch[1:]): s.put(stab(mi,.24,.09),b0+at+i*.02,-.3+.3*i,.055)
        for at in (.5,1.5,2.5,3.5):
            s.put(stab(ch[2],.12,.04),b0+at,.1,.02)
        s.put(kick(.7),b0,0,.26)
        for at in (1,3): s.put(wood(86),b0+at,.2,.07)
        for k in range(8): s.put(shaker(k%2==1),b0+k*.5,.3,.016 if k%2 else .009)
        if bar in (3,11):                                   # 새소리
            for j,(a,b) in enumerate(((3100,4100),(3500,4600),(3000,4300))):
                s.put(chirp(a,b),b0+3.0+j*.36,.45,.05)
        if bar in (7,15):                                   # 어린이집 종: 딩-동-댕
            for j,mi in enumerate((n('G6'),n('E6'),n('D6'))):
                s.put(glock(mi,.9),b0+2.0+j*.5,.3,.07)
    bars_loop16(s,prog,mel,pb); s.finish()

forest()
