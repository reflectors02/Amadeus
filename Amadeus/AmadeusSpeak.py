import subprocess
import platform
from pathlib import Path
from gradio_client import Client, handle_file


REF_WAV = Path("ttsout/kurisu10s.wav").resolve()
OUT_WAV = Path("ttsout/generated.wav").resolve()

# ======================
# GPT-SoVITS server
# ======================
GPTSOVITS_URL = "http://127.0.0.1:9872"

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Client(GPTSOVITS_URL)

        # REQUIRED once (UI does this automatically)
        _client.predict(api_name="/change_choices")
        _client.predict(
            "Use v2 base model directly without training!",
            api_name="/change_sovits_weights"
        )
        _client.predict(
            "Use v2 base model directly without training!",
            api_name="/change_gpt_weights"
        )
    return _client


def generateVoice(text: str):
    client = _get_client()

    wav_path = client.predict(
        handle_file(str(REF_WAV)),  # ref_wav_path
        "ん? ほっと来てくれませんか?ん? ふざけてないでちょっと来てくださいアニカって何ですか?人激の悪い私は", # prompt_text
        "Japanese",                 # prompt_language
        text,                       # text
        "Japanese",                 # text_language
        "",
        5,                          # top_k
        0.7,                        # top_p
        1.0,                        # temperature
        False,                      # ref_free
        1.0,                        # speed
        False,                      # if_freeze
        [],                         # inp_refs
        "32",                        # sample_steps
        True,                      # if_sr
        0.3,                        # pause_second
        api_name="/get_tts_wav"
    )

    OUT_WAV.write_bytes(Path(wav_path).read_bytes())


def play_sound():
    wav_path = str(OUT_WAV.resolve())
    system = platform.system()

    try:
        if system == "Darwin":
            subprocess.run(["afplay", wav_path], check=False)

        elif system == "Windows":
            subprocess.run([
                "powershell",
                "-NoProfile",
                "-Command",
                f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync();'
            ], check=False)

        else:
            for cmd in (
                ["paplay", wav_path],
                ["aplay", wav_path],
                ["ffplay", "-nodisp", "-autoexit", wav_path],
            ):
                try:
                    subprocess.run(cmd, check=False)
                    break
                except FileNotFoundError:
                    continue

    except Exception as e:
        print(f"[AmadeusSpeak] play_sound failed: {e}")
