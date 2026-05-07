"""music.py — Generate and play a Seinfeld-style slap-bass loop."""
import math, wave, struct, os, tempfile

def _make_wav(path: str) -> None:
    sr   = 22050
    dur  = 4.0
    n    = int(sr * dur)
    beat = sr // 4

    riff = [
        (82.4, 1), (98.0, 0.5), (110.0, 0.5),
        (123.5, 1), (110.0, 0.5), (98.0, 0.5),
        (82.4, 1), (82.4, 0.5), (98.0, 0.5),
        (110.0, 1), (98.0, 1),
    ]

    buf = [0.0] * n
    cur = 0
    for freq, beats in riff:
        ln = int(beat * beats)
        for i in range(ln):
            if cur + i >= n: break
            t  = i / sr
            e  = math.exp(-8 * t)
            v  = math.sin(2 * math.pi * freq * t) * e
            v += 0.4 * math.sin(4 * math.pi * freq * t) * math.exp(-12 * t)
            buf[cur + i] += v * 0.6
        cur += ln
        if cur >= n: break

    peak = max(abs(x) for x in buf) or 1.0
    pcm  = [int(x / peak * 28000) for x in buf]
    with wave.open(path, "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes(struct.pack(f"<{len(pcm)}h", *pcm))


def start(pygame) -> None:
    try:
        pygame.mixer.init(22050, -16, 1, 512)
        tmp = os.path.join(tempfile.gettempdir(), "sqcs_bass.wav")
        if not os.path.exists(tmp):
            _make_wav(tmp)
        pygame.mixer.music.load(tmp)
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(loops=-1)
    except Exception:
        pass
