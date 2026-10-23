"""문제풀이용 BGM 5곡 (sequencing · decomposition · branching · abstraction · pattern).
편안하지만 신나는 키즈앱 톤. 16마디 심리스 루프, 스테레오. 출력: <name>.wav (후처리로 mp3 + 음량 보정)"""
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

def bars_loop(song, prog, mel, per_bar):          # 8마디 구성을 2번 (A / A')
    for rep in range(2):
        for bar in range(8):
            b0=(rep*8+bar)*4
            per_bar(song, rep, bar, b0, prog[bar], mel[bar])

# ========== 1. SEQUENCING : 계단 오르듯 차근차근, 마림바 ==========
def seq():
    s=Song('puzzle-sequencing-stepping-loop',112,seed=11)
    C,Am,F,G,Em=([n('C3'),n('C4'),n('E4'),n('G4')],[n('A2'),n('C4'),n('E4'),n('A4')],
                 [n('F2'),n('C4'),n('F4'),n('A4')],[n('G2'),n('B3'),n('D4'),n('G4')],[n('E2'),n('B3'),n('E4'),n('G4')])
    prog=[C,Am,F,G,C,Em,F,G]
    up=lambda a:[(i*.5,n(x),.5) for i,x in enumerate(a)]
    mel=[up(['C5','D5','E5','G5','E5','D5','E5','C5']),
         up(['A4','B4','C5','E5','C5','B4','C5','A4']),
         up(['F4','G4','A4','C5','A4','G4','A4','C5']),
         [(0,n('D5'),.5),(.5,n('E5'),.5),(1,n('F5'),.5),(1.5,n('G5'),.5),(2,n('B5'),1.5),(3.5,n('G5'),.5)],
         up(['E5','F5','G5','C6','G5','F5','E5','G5']),
         up(['G4','A4','B4','E5','B4','A4','B4','G4']),
         up(['A4','C5','F5','A5','F5','C5','A4','C5']),
         [(0,n('B4'),.5),(.5,n('D5'),.5),(1,n('G5'),.5),(1.5,n('F5'),.5),(2,n('E5'),1),(3,n('C5'),1)]]
    def pb(s,rep,bar,b0,ch,m):
        for at,mi,ln in m:
            s.put(marimba(mi,ln*s.beat+.25),b0+at,-.12,.34*s.rng.uniform(.95,1.05))
            if rep==1: s.put(glock(mi+12,ln*s.beat+.4),b0+at,.25,.07)
        r=ch[0]
        for at,off in ((0,0),(1,7),(2,12),(3,7)):
            s.put(bass(r+off,.38,.2),b0+at,0,.34)
        for at in (1,3): s.put(stab(ch[1],.22),b0+at+.5,-.3,.05); s.put(stab(ch[2],.22),b0+at+.5,0,.05); s.put(stab(ch[3],.22),b0+at+.5,.3,.05)
        for at in (0,2): s.put(kick(),b0+at,0,.40)
        for at in (1,3): s.put(rim(),b0+at,.1,.06)
        for k in range(8): s.put(shaker(k%2==1),b0+k*.5,.3,.020 if k%2 else .012)
    bars_loop(s,prog,mel,pb); s.finish()

# ========== 2. DECOMPOSITION : 블록 쌓기, 오르골+피치카토 콜앤리스폰스 ==========
def deco():
    s=Song('puzzle-decomposition-blocks-loop',104,seed=22)
    F=[n('F2'),n('A3'),n('C4'),n('F4')]; Dm=[n('D2'),n('A3'),n('D4'),n('F4')]
    Bb=[n('Bb1'),n('F3'),n('Bb3'),n('D4')]; Cc=[n('C2'),n('G3'),n('C4'),n('E4')]; Am=[n('A1'),n('E3'),n('A3'),n('C4')]
    prog=[F,Dm,Bb,Cc,F,Am,Bb,Cc]
    # 짧은 스타카토 2~3음 '블록' 호출 / 낮은 음 응답
    def call(a,b,c): return [(0,n(a),.25),(.5,n(b),.25),(1,n(c),.5)]
    def resp(a,b,c): return [(2,n(a),.25),(2.5,n(b),.25),(3,n(c),.5)]
    mel=[call('A5','C6','F6')+resp('F5','A5','C6'),
         call('A5','D6','F6')+resp('D5','F5','A5'),
         call('F5','Bb5','D6')+resp('D5','F5','Bb5'),
         call('G5','C6','E6')+resp('E5','G5','C6'),
         call('A5','C6','F6')+resp('C6','A5','F5'),
         call('E5','A5','C6')+resp('A5','C6','E6'),
         call('F5','Bb5','D6')+resp('D6','Bb5','F5'),
         [(0,n('G5'),.5),(.5,n('E5'),.5),(1,n('C5'),.5),(1.5,n('E5'),.5),(2,n('G5'),.5),(2.5,n('C6'),.5),(3,n('C6'),1)]]
    def pb(s,rep,bar,b0,ch,m):
        for at,mi,ln in m:
            hi = at<2 or bar==7
            s.put(musicbox(mi,ln*s.beat+.35),b0+at,-.15 if hi else .15,.30 if hi else .26)
            if rep==1 and not hi: s.put(pizz(mi-12,.3),b0+at,.1,.18)
        r=ch[0]
        for at,off,ln in ((0,0,.45),(1,0,.4),(1.5,7,.4),(2,0,.45),(3,7,.4),(3.5,12,.4)):
            s.put(pizz(r+off+12,.3) if False else bass(r+off,ln*s.beat+.1,.16),b0+at,0,.34)
        for at in (.5,2.5):
            for i,mi in enumerate(ch[1:]): s.put(stab(mi,.18,.06),b0+at+.5,-.3+.3*i,.05)
        s.put(kick(),b0,0,.38); s.put(kick(.8),b0+2.5,0,.30)
        for at in (1,3): s.put(wood(88),b0+at,.2,.10);
        for k in range(8): s.put(shaker(k%2==1),b0+k*.5,.3,.016)
    bars_loop(s,prog,mel,pb); s.finish()

# ========== 3. BRANCHING : 갈림길, 셔플 + 질문/대답 프레이즈 ==========
def branch():
    s=Song('puzzle-branching-crossroads-loop',108,seed=33,swing=0.17)
    G=[n('G2'),n('B3'),n('D4'),n('G4')]; Em=[n('E2'),n('B3'),n('E4'),n('G4')]
    C=[n('C2'),n('G3'),n('C4'),n('E4')]; D=[n('D2'),n('A3'),n('D4'),n('F#4')]; Bm=[n('B1'),n('F#3'),n('B3'),n('D4')]
    prog=[G,Em,C,D,G,Bm,C,D]
    q=lambda *x:[(i*.5 if i<4 else 2+(i-4)*.5,n(v),.5) for i,v in enumerate(x)]
    mel=[[(0,n('G4'),.5),(.5,n('B4'),.5),(1,n('D5'),1),(2.5,n('E5'),.5),(3,n('D5'),1)],      # 질문(열린 끝: D)
         [(0,n('E5'),.5),(.5,n('D5'),.5),(1,n('B4'),1),(2.5,n('A4'),.5),(3,n('B4'),1)],
         [(0,n('C5'),.5),(.5,n('E5'),.5),(1,n('G5'),1),(2.5,n('F#5'),.5),(3,n('A5'),1)],
         [(0,n('G5'),.5),(.5,n('F#5'),.5),(1,n('D5'),1),(2.5,n('A4'),.5),(3,n('D5'),1)],
         [(0,n('G4'),.5),(.5,n('B4'),.5),(1,n('D5'),1),(2.5,n('G5'),.5),(3,n('F#5'),1)],      # 대답(닫힘: G)
         [(0,n('D5'),.5),(.5,n('F#5'),.5),(1,n('B5'),1),(2.5,n('A5'),.5),(3,n('F#5'),1)],
         [(0,n('E5'),.5),(.5,n('G5'),.5),(1,n('C6'),1),(2.5,n('B5'),.5),(3,n('A5'),1)],
         [(0,n('B5'),.5),(.5,n('A5'),.5),(1,n('G5'),1),(2,n('D5'),1),(3,n('G5'),1)]]
    def pb(s,rep,bar,b0,ch,m):
        for at,mi,ln in m:
            s.put(pluck(mi,ln*s.beat+.3,1.1),b0+at,-.1,.34)
            if rep==1: s.put(glock(mi+12,ln*s.beat+.4),b0+at,.25,.07)
        r=ch[0]
        for at,off,ln in ((0,0,.9),(1.5,12,.45),(2,0,.9),(3.5,7,.45)):
            s.put(bass(r+off,ln*s.beat+.1),b0+at,0,.36)
        # 우쿨렐레 스트럼 느낌: 2,4박 하향
        for at in (1,3):
            for i,mi in enumerate(ch[1:]): s.put(stab(mi,.26,.10),b0+at+i*.02,-.3+.3*i,.06)
        s.put(kick(),b0,0,.40); s.put(kick(.8),b0+2,0,.34)
        for at in (1,3): s.put(clap(),b0+at,.1,.05)
        for k in range(8): s.put(shaker(k%2==1),b0+k*.5,.3,.020 if k%2 else .012)
    bars_loop(s,prog,mel,pb); s.finish()

# ========== 4. ABSTRACTION : 몽글몽글 패드 + 글로켄슈필, 가장 차분 ==========
def abstr():
    s=Song('puzzle-abstraction-dreamy-loop',92,seed=44)
    D=[n('D3'),n('A3'),n('D4'),n('F#4')]; Bm=[n('B2'),n('F#3'),n('B3'),n('D4')]
    G=[n('G2'),n('D3'),n('B3'),n('D4')]; A=[n('A2'),n('E3'),n('A3'),n('C#4')]; Fm=[n('F#2'),n('C#3'),n('A3'),n('C#4')]
    prog=[D,Bm,G,A,D,Fm,G,A]
    mel=[[(0,n('A5'),1.5),(1.5,n('F#5'),.5),(2,n('D6'),2)],
         [(0,n('B5'),1),(1,n('A5'),1),(2,n('F#5'),2)],
         [(0,n('G5'),1.5),(1.5,n('B5'),.5),(2,n('D6'),2)],
         [(0,n('C#6'),1),(1,n('A5'),1),(2,n('E5'),2)],
         [(0,n('F#5'),1),(1,n('A5'),1),(2,n('D6'),1),(3,n('E6'),1)],
         [(0,n('F#6'),1.5),(1.5,n('E6'),.5),(2,n('C#6'),2)],
         [(0,n('B5'),1),(1,n('D6'),1),(2,n('G6'),1),(3,n('F#6'),1)],
         [(0,n('E6'),1.5),(1.5,n('C#6'),.5),(2,n('A5'),2)]]
    def pb(s,rep,bar,b0,ch,m):
        s.put(pad(ch,4*s.beat+.4),b0,0,.55)
        for at,mi,ln in m:
            s.put(glock(mi,ln*s.beat+.5),b0+at,-.15,.30)
            if rep==1: s.put(musicbox(mi-12,ln*s.beat+.4),b0+at+.5,.2,.10)
        r=ch[0]
        for at,off in ((0,0),(2,7)): s.put(bass(r+off,.6,.35),b0+at,0,.34)
        # 도레미 아르페지오 반짝임(약하게)
        for i,mi in enumerate((ch[1],ch[2],ch[3],ch[2])): s.put(pluck(mi+12,.3,.8),b0+i+.5,.2,.06)
        s.put(kick(.8),b0,0,.30)
        for k in (1,3): s.put(shaker(True),b0+k,.3,.014)
        for k in range(8): s.put(shaker(False),b0+k*.5,.3,.007)
    bars_loop(s,prog,mel,pb); s.finish()

# ========== 5. PATTERN : 반복 모티프(오스티나토) + 통통 튀는 베이스 ==========
def patt():
    s=Song('puzzle-pattern-groove-loop',116,seed=55)
    A=[n('A2'),n('A3'),n('C#4'),n('E4')]; Fm=[n('F#2'),n('A3'),n('C#4'),n('F#4')]
    D=[n('D2'),n('A3'),n('D4'),n('F#4')]; E=[n('E2'),n('B3'),n('E4'),n('G#4')]
    prog=[A,Fm,D,E,A,Fm,D,E]
    motif=lambda a,b,c,d:[(0,n(a),.5),(.5,n(b),.5),(1,n(c),.5),(1.5,n(b),.5),(2,n(d),.5),(2.5,n(c),.5),(3,n(b),1)]
    mel=[motif('A4','C#5','E5','A5'),motif('A4','C#5','E5','A5'),                     # 같은 모티프 반복
         motif('A4','D5','F#5','A5'),motif('G#4','B4','E5','G#5'),
         motif('A4','C#5','E5','A5'),motif('A4','C#5','F#5','A5'),                     # 살짝 변주
         motif('A4','D5','F#5','B5'),[(0,n('B5'),.5),(.5,n('G#5'),.5),(1,n('E5'),.5),(1.5,n('G#5'),.5),(2,n('A5'),2)]]
    def pb(s,rep,bar,b0,ch,m):
        for at,mi,ln in m:
            s.put(marimba(mi,ln*s.beat+.25),b0+at,-.12,.33*s.rng.uniform(.96,1.04))
            if rep==1: s.put(glock(mi+12,ln*s.beat+.4),b0+at,.25,.07)
        r=ch[0]
        for at,off,ln in ((0,0,.45),(.75,0,.3),(1.5,12,.35),(2,0,.45),(2.75,7,.3),(3.5,12,.35)):
            s.put(bass(r+off,ln*s.beat+.1,.14),b0+at,0,.36)
        for at in (.5,1.5,2.5,3.5):
            for i,mi in enumerate(ch[1:]): s.put(stab(mi,.18,.06),b0+at,-.3+.3*i,.05)
        for at in (0,2): s.put(kick(),b0+at,0,.40)
        for at in (1,3): s.put(clap(),b0+at,.1,.05)
        for k in range(8): s.put(shaker(k%2==1),b0+k*.5,.3,.020 if k%2 else .012)
    bars_loop(s,prog,mel,pb); s.finish()

for f in (seq,deco,branch,abstr,patt): f()
