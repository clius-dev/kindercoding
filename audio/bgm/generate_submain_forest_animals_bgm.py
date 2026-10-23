"""서브메인(B-3_00.submain) 숲속 동물 BGM v2 — submain-forest-animals-loop. 발랄·율동 (118bpm, 스타카토 마림바 리드 + 오프비트 스트럼 + 오음 베이스).
합성기는 generate_submain_bgm.py 를 그대로 가져다 쓴다.
사용: python generate_submain_forest_animals_bgm.py <출력폴더> → wav (후처리: ffmpeg loudnorm I=-18 · 160k mp3)"""
import sys
from pathlib import Path
src=(Path(__file__).parent/'generate_submain_bgm.py').read_text(encoding='utf-8')
lib=src[:src.index('def meadow():')]
exec(compile(lib,'lib','exec'))

def forest():
    s=Song('submain-forest-animals-loop',118,seed=33,swing=0.05)
    G =[n('G2'),n('B3'),n('D4'),n('G4')]; D =[n('D3'),n('A3'),n('D4'),n('F#4')]
    Em=[n('E2'),n('B3'),n('E4'),n('G4')]; C =[n('C3'),n('G3'),n('C4'),n('E4')]
    Am=[n('A2'),n('E4'),n('A4'),n('C5')]
    prog=[G,Em,C,D, G,Em,C,D,   C,G,Am,D, C,G,D,G]
    X=None
    L=[['D5','G5','B5','G5','D6','B5','G5',X],
       ['E5','G5','B5','G5','E6','B5','G5',X],
       ['E5','G5','C6','G5','E6','C6','G5',X],
       ['F#5','A5','D6','A5','C#6','A5','F#5',X],
       ['G5',X,'B5','D6',X,'B5','A5','G5'],
       ['G5',X,'B5','E6',X,'D6','B5','G5'],
       ['E5','G5','C6',X,'B5','A5','G5','E5'],
       ['A5','F#5','D5',X,'F#5','A5','C#6','D6'],
       ['C6',X,'G5','E5','G5',X,'C6','E6'],
       ['D6',X,'B5','G5','B5',X,'D6','G6'],
       ['C6',X,'A5','E5','A5','C6','E6','C6'],
       ['D6','C#6','A5','F#5','A5','D6',X,X],
       ['E6',X,'C6','G5','E6','D6','C6',X],
       ['D6',X,'B5','G5','D6','B5','G5',X],
       ['A5',X,'F#5','A5','D6','C#6','A5','F#5'],
       ['G5','B5','D6','B5','G5',X,'D5',X]]
    def pb(s,rep,bar,b0,ch,m):
        s.put(pad(ch[1:],4*s.beat+.2),b0,0,.10)                                    # 아주 얇은 배경 패드
        for k,nt in enumerate(L[bar]):
            if nt is None: continue
            mi=n(nt); acc=1.0 if k%2==0 else .85
            s.put(marimba(mi,.30),b0+k*.5,-.1,.30*acc*s.rng.uniform(.95,1.05))     # 스타카토 리드
            if rep==1: s.put(glock(mi+12,.3),b0+k*.5,.3,.07)                       # B: 글로켄 반짝임
        r=ch[0]
        for at,off,ln in ((0,0,.35),(1,7,.3),(2,0,.35),(3,7,.3)):                  # 통통 튀는 루트-5도 베이스
            s.put(bass(r+off,ln*s.beat+.05,.14),b0+at,0,.34)
        for at in (.5,1.5,2.5,3.5):                                                # 오프비트 기타 스트럼 (율동)
            for i,mi in enumerate(ch[1:]): s.put(stab(mi,.18,.05),b0+at+i*.012,-.35+.35*i,.055)
        s.put(kick(.6),b0,0,.22); s.put(kick(.5),b0+2,0,.20); s.put(kick(.3),b0+3.5,0,.08)
        for at in (1,3): s.put(wood(86),b0+at,.2,.08); s.put(rim(),b0+at,-.2,.03)
        for k in range(16): s.put(shaker(k%4==2),b0+k*.25,.3,.016 if k%2 else .010)
        if bar in (3,7,11,15):                                                      # 짧은 새소리 (마디 끝)
            for j,(a,b) in enumerate(((3000,4200),(3500,4600))):
                s.put(chirp(a,b,.09),b0+3.25+j*.25,.45,.04)
    bars_loop16(s,prog,L,pb); s.finish()
forest()
