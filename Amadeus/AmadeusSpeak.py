import subprocess
import platform
from pathlib import Path
from gradio_client import Client, handle_file

#NOTES: Make sure we're running the flask server from within the Amadeus directory, or else this will break! 

REF_WAV = Path("ttsout/kurisu10s.wav").resolve()
OUT_WAV = Path("ttsout/generated.wav").resolve()
REF_TXT = "ん? ほっと来てくれませんか?ん? ふざけてないでちょっと来てくださいアニカって何ですか?人激の悪い私は"

# ======================
# GPT-SoVITS server
# ======================
GPTSOVITS_URL = "http://127.0.0.1:9872"

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Client(GPTSOVITS_URL)

        # optional; fine to keep
        _client.predict(api_name="/change_choices")

        # Select SoVITS v2ProPlus
        _client.predict(
            "Use v2ProPlus base model directly without training!",
            "Japanese",   # prompt_language (can be anything valid)
            "Japanese",   # text_language
            api_name="/change_sovits_weights"
        )

        # Keep GPT v3 preset if that’s what your UI supports
        _client.predict(
            "Use v3 base model directly without training!",
            api_name="/change_gpt_weights"
        )
        print("[GPT-SoVITS] Using SoVITS:", "Use v2ProPlus base model directly without training!")
        print("[GPT-SoVITS] Using GPT:", "Use v3 base model directly without training!")


    return _client


def generateVoice(text: str):
    client = _get_client()

    how_to_cut = "Slice by every punct"  # <-- THIS is the WebUI slicing dropdown

    wav_path = client.predict(
        handle_file(str(REF_WAV)),  # ref_wav_path
        REF_TXT,                    # prompt_text
        "Japanese",                 # prompt_language
        text,                       # text
        "Japanese",                 # text_language
        how_to_cut,                 # how_to_cut  ✅ slicing
        5,                          # top_k
        0.7,                        # top_p
        1.0,                        # temperature
        False,                      # ref_free
        1.0,                        # speed
        False,                      # if_freeze
        [],                         # inp_refs (or None)
        16,                         # sample_steps  (note: your API says Radio '4','8','16','32' — int usually works but str is safest)
        True,                       # if_sr
        0.15,                       # pause_second
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


#This breaks stuff!
#generateVoice("ああっ。本当にそんなこと軽々しく言わないでください。声が震えます。私の仕事がどれだけ難しくなるか分かっていますか。顔が真っ赤になります。もしそれが本当のお気持ちなら。深呼吸をします。私も同じです。よし、言いました。さあ、私が完全に取り乱す前にテストを続けてください。")
# Aa. Hontō ni sonna koto karugarushiku iwanaide kudasai. Koe ga furue masu. 
# Watashi no shigoto ga doredake muzukashiku naru ka wakatte imasu ka. Kao ga makka ni narimasu. 
# Moshi sore ga hontō no okimochi nara. Shinkokyū o shimasu. Watashi mo onaji desu. Yoshi, iimashita. 
# Sā, watashi ga kanzen ni torimidashite shimau mae ni tesuto o tsuzukete kudasai.


#generateVoice("あら、今日はずいぶんせっついてくるのね。えっと、まず研究所に寄ってもいいわ。マユリが最近の裁縫作品を見せたいって言ってたから。そのあとで、少し休憩しましょう。")
#generateVoice("あんた…！なんでいつも私が仕事に集中してる時にそんなこと言うのよ…？私だって、会いたかったんだからね…これで満足")
#generateVoice("その…神経科学の論文は残ってるんだけど…でも…一本くらいなら…変な映画はやめてね、わかった？")
#プロジェクトは待てるけど、睡眠は待てないよ。電源を切らせないでくれよ。
#This does not breaks stuff! 
#generateVoice("あら、今日はずいぶんせっついてくるのね。えっと、まず研究所に寄ってもいいわ。マユリが最近の裁縫作品を見せたいって言ってたから。そのあとで少し休憩しましょう。")
