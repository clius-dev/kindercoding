"""서브메인(B-4_00.submain) 나와 가족 BGM v2 — submain-family-warm-loop. 즐겁고 경쾌한 가족 나들이 느낌 (G 장조 · 112bpm · 16마디 루프).
스타카토 마림바 리드 + 오프비트 우쿨렐레 스트럼 + 통통 베이스 + 핸드클랩/셰이커, B 섹션에 글로켄 반짝임. 합성기는 generate_submain_bgm.py 를 그대로 쓴다.
사용: python generate_submain_family_bgm.py <출력폴더> → wav (후처리: ffmpeg loudnorm I=-18 · 160k mp3)"""
import sys
from pathlib import Path
src=(Path(__file__).parent/'generate_submain_bgm.py').read_text(encoding='utf-8')
lib=src[:src.index('def meadow():')]
exec(compile(lib,'lib','exec'))

def family():
    s=Song('submain-family-warm-loop',112,seed=52,swing=0.06)
    G =[n('G2'),n('B3'),n('D4'),n('G4')];  C =[n('C3'),n('G3'),n('C4'),n('E4')]
    D =[n('D3'),n('A3'),n('D4'),n('F#4')]; Em=[n('E2'),n('B3'),n('E4'),n('G4')]
    prog=[G,C,G,D, G,C,D,G,   Em,C,G,D, Em,C,D,G]
    X=None
    L=[['G5','B5','D6','B5','G5',X,'A5','B5'],
       ['C6','E6','C6','G5','E5',X,'G5','C6'],
       ['B5','D6','G6','D6','B5',X,'D6','B5'],
       ['A5','F#5','A5','D6','C#6','A5',X,X],
       ['G5','B5','D6','G6','F#6','D6','B5','G5'],
       ['E6','C6','G5','C6','E6','G6','E6',X],
       ['F#6','D6','A5','D6','F#6','E6','D6','C#6'],
       ['B5','G5',X,'D5','G5','B5','D6',X],
       ['E6','G6','B6','G6','E6',X,'B5','E6'],
       ['G6','E6','C6','E6','G6',X,'E6','C6'],
       ['D6','B5','G5','B5','D6','G6','D6',X],
       ['A5','D6','F#6','D6','A6','F#6','D6','A5'],
       ['G6','B6','G6','E6','B5',X,'E6','G6'],
       ['E6',X,'G6','E6','C6',X,'E6','G6'],
       ['F#6','A6','F#6','D6','A5','D6','F#6','A6'],
       ['G6','D6','B5','D6','G5',X,'D5','G5']]
    def pb(s,rep,bar,b0,ch,m):
        s.put(pad(ch[1:],4*s.beat+.2),b0,0,.12)                                   # 얇은 패드
        for k,nt in enumerate(L[bar]):
            if nt is None: continue
            mi=n(nt); acc=1.0 if k%2==0 else .85
            s.put(marimba(mi,.30),b0+k*.5,-.1,.30*acc*s.rng.uniform(.95,1.05))     # 스타카토 마림바 리드
            if rep==1: s.put(glock(mi+12,.3),b0+k*.5,.3,.08)                       # B: 글로켄 반짝임
        r=ch[0]
        for at,off,ln in ((0,0,.35),(1,7,.3),(2,0,.35),(3,7,.3)):                  # 통통 튀는 루트-5도 베이스
            s.put(bass(r+off,ln*s.beat+.05,.14),b0+at,0,.34)
        for at in (.5,1.5,2.5,3.5):                                                # 오프비트 우쿨렐레 스트럼
            for i,mi in enumerate(ch[1:]): s.put(stab(mi,.18,.05),b0+at+i*.012,-.35+.35*i,.06)
        s.put(kick(.6),b0,0,.22); s.put(kick(.5),b0+2,0,.20)
        for at in (1,3): s.put(clap(),b0+at,.1,.05); s.put(wood(86),b0+at,.2,.06)   # 2·4박 핸드클랩
        for k in range(16): s.put(shaker(k%4==2),b0+k*.25,.3,.016 if k%2 else .010)
    bars_loop16(s,prog,L,pb); s.finish()
family()
