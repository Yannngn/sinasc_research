import argparse
import io
import json
import os
import zipfile

import pandas as pd
import requests
from tqdm import tqdm


def download_and_process_cnes_json(
    json_path: str = "data/CNES/estabelecimentos_cnes.json", csv_path: str = "data/CNES/estabelecimentos_cnes_flat.csv"
) -> None:
    """
    Download and process CNES establishments data from DATASUS JSON.
    If JSON exists, load it; otherwise, download and extract from ZIP.
    Then create a flat CSV from the JSON.
    """
    print("Iniciando o processo de busca e criação da tabela de estabelecimentos do CNES...")

    # URL do arquivo ZIP do CNES JSON.
    # Nota: O DATASUS atualiza os links mensalmente. Este link é de Set/2025.
    # Se o link quebrar, você pode encontrar o mais recente no portal DATASUS.
    url = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/CNES/cnes_estabelecimentos_json.zip"

    # Colunas de interesse que vamos extrair do JSON original.
    colunas_de_interesse = [
        "CO_CNES",
        "CO_UNIDADE",
        "CO_UF",
        "CO_IBGE",
        "NO_FANTASIA",
        "TP_UNIDADE",
        "CO_CEP",
        "NO_LOGRADOURO",
        "NO_BAIRRO",
        "NU_LATITUDE",
        "NU_LONGITUDE",
    ]

    try:
        # Verifica se o JSON já existe
        if os.path.exists(json_path):
            print(f"JSON já existe em {json_path}. Carregando...")
            with open(json_path, "r", encoding="utf-8") as f:
                estabelecimentos = json.load(f)
        else:
            print(f"Baixando o arquivo de: {url}")
            # Faz o request para a URL
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Verifica se o download foi bem-sucedido (código 200)

            print("Download completo. Descompactando e lendo o JSON em memória...")

            # Usa 'io.BytesIO' para tratar o conteúdo baixado como um arquivo em memória
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Pega o nome do primeiro arquivo dentro do ZIP (geralmente o único)
                nome_arquivo_json = z.namelist()[0]

                with z.open(nome_arquivo_json) as f:
                    estabelecimentos = json.load(f)

            # Salva o JSON extraído para uso futuro
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(estabelecimentos, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON salvo em {json_path}")

        print("JSON carregado com sucesso. Transformando para CSV flat...")

        # Cria o CSV flat
        with open(csv_path, "w", encoding="utf-8") as f:
            # Cabeçalho
            header = ",".join(colunas_de_interesse) + "\n"
            f.write(header)

            # Processa cada estabelecimento
            runner = tqdm(estabelecimentos, total=len(estabelecimentos), desc="Processing establishments", unit="est")
            for est in estabelecimentos:
                runner.desc = f"Processing {est.get('NO_FANTASIA', 'Unknown')}"

                # Extrai apenas as colunas de interesse
                row = [str(est.get(col, "")) for col in colunas_de_interesse]
                f.write(",".join(row) + "\n")
                runner.update(1)

            runner.close()

        print(f"✅ CSV flat criado em {csv_path}")

        # Carrega o CSV para exibir informações (opcional)
        df_cnes = pd.read_csv(csv_path, dtype=str)
        print("\n--- Tabela de Estabelecimentos de Saúde (CNES) Criada ---")

        # Exibe as 5 primeiras linhas do DataFrame
        print("\n### Amostra dos Dados:")
        print(df_cnes.head())

        # Exibe informações sobre o DataFrame (tipos de dados, memória usada, etc.)
        print("\n### Informações da Tabela:")
        df_cnes.info()
        print(df_cnes.memory_usage(deep=True))

    except requests.exceptions.RequestException as e:
        print(f"\nErro ao baixar o arquivo: {e}")
        print("Verifique sua conexão com a internet ou se a URL ainda é válida no portal DATASUS.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and process CNES establishments JSON data.")
    parser.add_argument("--json_output", default="data/CNES/estabelecimentos_cnes.json", help="Output JSON file path")
    parser.add_argument("--csv_output", default="data/CNES/estabelecimentos_cnes_flat.csv", help="Output CSV file path")
    args = parser.parse_args()

    download_and_process_cnes_json(args.json_output, args.csv_output)
