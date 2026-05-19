from openai import OpenAI
import openai

client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it', 
    api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A'
)

print("Enviando mensagem para o Gemma 3 12B...")

try:
    resp = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=[{'role': 'user', 'content': 'Hi'}],
    )
    print("\n[Sucesso] Resposta do modelo:")
    print(resp.choices[0].message.content)

except openai.InternalServerError as e:
    print("\n[Erro 503] O servidor da universidade está offline ou reiniciando.\nAguarde alguns instantes e tente novamente.\n")
    print("Aguarde alguns instantes e tente novamente.")
except Exception as e:
    print(f"\nErro inesperado: {e}")