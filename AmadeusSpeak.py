import soundfile as sf           # pip install soundfile
import LangSegment

# Create the missing aliases for backward-compatibility:
LangSegment.setLangfilters = LangSegment.setfilters
LangSegment.getLangfilters = LangSegment.getfilters

from gpt_sovits_python import TTS, TTS_Config
import subprocess
import os

soviets_configs = {
    "default": {
        "device": "cpu",  #  ["cpu", "cuda"]
        "is_half": False,  #  Set 'False' if you will use cpu
        "t2s_weights_path": "pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt",
        "vits_weights_path": "pretrained_models/s2G488k.pth",
        "cnhuhbert_base_path": "pretrained_models/chinese-hubert-base",
        "bert_base_path": "pretrained_models/chinese-roberta-wwm-ext-large"
    }
}

tts_config = TTS_Config(soviets_configs)
tts_pipeline = TTS(tts_config)

def generateVoice(response):
    params = {
        "text": response,                   # str.(required) text to be synthesized
        "text_lang": "ja",            # str.(required) language of the text to be synthesized [, "en", "zh", "ja", "all_zh", "all_ja"] 
        "ref_audio_path":"ttsout/kurisu10s.wav",         # str.(required) reference audio path
        "prompt_text": "ん? ほっと来てくれませんか?ん? ふざけてないでちょっと来てくださいアニカって何ですか?人激の悪い私は",            # str.(optional) prompt text for the reference audio
        "prompt_lang": "ja",            # str.(required) language of the prompt text for the reference audio
        "top_k": 5,                   # int. top k sampling
        "top_p": 1,                   # float. top p sampling
        "temperature": 1,             # float. temperature for sampling
        "speed_factor": 1.0,          # float. control the speed of the synthesized audio.
        "media_type": "wav",          # str. media type of the output audio, support "wav", "raw", "ogg", "aac".
        "out_path": "ttsout/generated.wav"
        }
    
    # 1) run() returns a generator of (sample_rate, numpy_array) tuples
    audio_gen = tts_pipeline.run(params)

    # 2) grab the first (and only) chunk
    sr, wav = next(audio_gen)

    # 3) write it to disk
    sf.write("ttsout/generated.wav", wav, sr)

def play_sound():
    subprocess.run(["afplay", "ttsout/generated.wav"])


#generateVoice("ほっと来てくれませんか?ん?")
