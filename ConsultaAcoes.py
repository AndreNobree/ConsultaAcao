import requests
from lxml import html
import time
import datetime
from win10toast import ToastNotifier

toaster = ToastNotifier()

def fazer_solicitacao(url, nome_acao):
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            headers = {'Cache-Control': 'no-cache'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Lança exceção se o status HTTP não for 200
        except requests.exceptions.RequestException as e:
            print(f'Tentativa {tentativa + 1} de {max_tentativas}: Erro de rede ao recuperar a página {nome_acao}: {e}')
        except requests.exceptions.HTTPError as e:
            print(f'Tentativa {tentativa + 1} de {max_tentativas}: Erro HTTP ao recuperar a página {nome_acao}: {e}')
        else:
            return response
        if tentativa < max_tentativas - 1:
            time.sleep(5)  # Espera 5 segundos antes de tentar novamente

    print(f'Todas as {max_tentativas} tentativas falharam para {nome_acao}')
    return None

def calcular_porcentagem_ganho_perda(resultado, cota_compra):
    porcentagem = ((resultado - cota_compra) / cota_compra) * 100
    return round(porcentagem, 2)

def exibir_notificacao(nome_acao, valor, margem):
    toaster.show_toast(f"{nome_acao}: R${valor} {margem}", threaded=True, icon_path=None, duration=10)

def monitorar_acoes():
    acoes = [
        {"nome": "GALG11", "url": 'https://br.investing.com/equities/guardian-logistica', "cotaCompra": 9.24},
        {"nome": "VINO11", "url": 'https://br.investing.com/equities/vinci-offices-fdo-inv-imob', "cotaCompra": 8.34},
        {"nome": "VGHF11", "url": 'https://br.investing.com/equities/valora-instrumentos-financeiros-fii', "cotaCompra": 9.54}
    ]

    while True:
        agora = datetime.datetime.now()
        hora = agora.hour
        minuto = agora.minute

        if hora > 9 and hora < 17:
            for acao in acoes:
                response = fazer_solicitacao(acao["url"], acao["nome"])

                if response is not None and response.status_code == 200:
                    tree = html.fromstring(response.content)
                    elemento = tree.xpath('//*[@id="__next"]/div[2]/div[2]/div[1]/div[1]/div[3]/div/div[1]/div[1]/div[1]')

                    if elemento:
                        valor = float(elemento[0].text.replace(",", "."))
                        resultado = valor - acao["cotaCompra"]
                        resultado = round(resultado, 3)
                        porcentagem = calcular_porcentagem_ganho_perda(valor, acao["cotaCompra"])

                        if resultado < 0:
                            margem = f"sua Perda é de R${resultado} ({porcentagem}%)"
                        else:
                            margem = f"seu Ganho é de R${resultado} ({porcentagem}%)"

                        if hora == 10 and minuto <= 30:
                            print(f'Registrado na hora {hora}:{minuto} - {acao["nome"]}: R${valor} {margem}')
                            exibir_notificacao(f"Iniciando ({acao['nome']})", valor, margem)
                            time.sleep(20)
                        elif abs(porcentagem) >= 2:
                            print(f"({acao['nome']}): R${valor} {margem}")
                            exibir_notificacao(acao["nome"], valor, margem)
                            time.sleep(20)
                        else:
                            time.sleep(5)
                    else:
                        print(f'Elemento desejado não encontrado na página da ação {acao["nome"]}')
                else:
                    print(f'Falha ao recuperar a página {acao["nome"]}:', response.status_code)

                time.sleep(20)
        else:
            time.sleep(1800)  # Espera 30 minutos fora do horário de negociação

if __name__ == "__main__":
    monitorar_acoes()
