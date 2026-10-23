"""서브메인(B-5_00.submain) 우리 동네 BGM — submain-town-walk-loop. 신나는 동네 산책·나들이 느낌 (D 장조 · 120bpm · 16마디 루프).
통통 걷는 베이스 + 또각또각 우드블록(발걸음) + 스타카토 마림바 리드 + 오프비트 우쿨렐레 + 핸드클랩/셰이커, B 섹션에 글로켄 반짝임, 7·15마디 끝에 새소리.
합성기는 generate_submain_bgm.py 를 그대로 쓴다.
사용: python generate_submain_town_bgm.py <출력폴더> → wav (후처리: ffmpeg loudnorm I=-18 · 160k mp3)"""
import sys
from pathlib import Path
src=(Path(__file__).parent/'generate_submain_bgm.py').read_text(encoding='utf-8')
lib=src[:src.index('def meadow():')]
exec(compile(lib,'lib','exec'))

def town():
    s=Song('submain-town-walk-loop',120,seed=95,swing=0.05)
    D =[n('D3'),n('A3'),n('D4'),n('F#4')]; G =[n('G2'),n('B3'),n('D4'),n('G4')]
    A =[n('A2'),n('A3'),n('C#4'),n('E4')]; Bm=[n('B2'),n('B3'),n('D4'),n('F#4')]
    prog=[D,G,D,A, D,G,A,D,   Bm,G,D,A, Bm,G,A,D]
    X=None
    L=[['F#5','A5','A5','D6','A5','F#5','A5','B5'],
       ['B5','D6','D6','B5','G5',X,'B5','D6'],
       ['A5','F#5','A5','D6','C#6','A5','F#5',X],
       ['E6','C#6','A5','C#6','E6',X,'D6','C#6'],
       ['D6','F#6','A6','F#6','D6',X,'A5','D6'],
       ['B5','D6','G6','D6','B5','G5','B5','D6'],
       ['C#6','E6','A6','E6','C#6','A5',X,'C#6'],
       ['D6','A5','F#5',X,'D5','F#5','A5',X],
       ['B5','D6','F#6','D6','B5',X,'F#5','B5'],
       ['G5','B5','D6','B5','G6','D6','B5',X],
       ['F#6','D6','A5','D6','F#6','A6','F#6',X],
       ['E6','C#6','A5','E6','A6','E6','C#6','A5'],
       ['D6','F#6','B6','F#6','D6',X,'B5','D6'],
       ['B5','D6','G6','B6','G6','D6','B5','G5'],
       ['A6','E6','C#6','E6','A6',X,'E6','C#6'],
       ['D6','F#6','A5','D6','F#5',X,'A5','D5']]
    def pb(s,rep,bar,b0,ch,m):
        s.put(pad(ch[1:],4*s.beat+.2),b0,0,.11)                                   # 얇은 패드
        for k,nt in enumerate(L[bar]):
            if nt is None: continue
            mi=n(nt); acc=1.0 if k%2==0 else .85
            s.put(marimba(mi,.28),b0+k*.5,-.1,.30*acc*s.rng.uniform(.95,1.05))     # 스타카토 마림바 리드
            if rep==1: s.put(glock(mi+12,.3),b0+k*.5,.3,.08)                       # B: 글로켄 반짝임
        r=ch[0]
        for at,off,ln in ((0,0,.30),(1,7,.28),(2,12,.30),(3,7,.28)):               # 걷는 듯 통통 베이스 (근음-5도-옥타브-5도)
            s.put(bass(r+off,ln*s.beat+.05,.13),b0+at,0,.33)
        for at in (.5,1.5,2.5,3.5):                                                # 오프비트 우쿨렐레 스트럼
            for i,mi in enumerate(ch[1:]): s.put(stab(mi,.16,.05),b0+at+i*.012,-.35+.35*i,.06)
        s.put(kick(.6),b0,0,.22); s.put(kick(.5),b0+2,0,.20)
        for at in (1,3): s.put(clap(),b0+at,.1,.05)                                 # 2·4박 핸드클랩
        for at,m_ in ((0,88),(1,82),(2,88),(3,82)): s.put(wood(m_),b0+at,.2,.05)    # 또각또각 발걸음
        for k in range(16): s.put(shaker(k%4==2),b0+k*.25,.3,.016 if k%2 else .010)
        if bar in (7,15):                                                          # 새소리 (마지막 마디 끝)
            for j,(a,b) in enumerate(((3100,4100),(3500,4600))):
                s.put(chirp(a,b),b0+3.0+j*.4,.45,.045)
    bars_loop16(s,prog,L,pb); s.finish()
town()
