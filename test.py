from gradio_client import Client
GPTSOVITS_URL = "http://127.0.0.1:9872"

client = Client(GPTSOVITS_URL)

# Shows every endpoint and its parameter list (names + order)
print(client.view_api(return_format="dict")["named_endpoints"]["/get_tts_wav"])
