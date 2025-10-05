import io
import json
import os
import zipfile

import pandas as pd
import requests

CNES_API = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/CNES/cnes_estabelecimentos_json.zip"


CNES_COLUMNS = [
    "CO_CNES",
    "CO_UNIDADE",
    "CO_UF",
    "CO_IBGE",
    "CO_NATUREZA_JUR",
    "NO_FANTASIA",
    "TP_UNIDADE",
    "CO_CEP",
    "NO_LOGRADOURO",
    "NO_BAIRRO",
    "NU_LATITUDE",
    "NU_LONGITUDE",
    "ST_CENTRO_OBSTETRICO",
]


def _request(outpath: str = "data/CNES/estabelecimentos_cnes.json"):
    response = requests.get(CNES_API)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Pega o nome do primeiro arquivo dentro do ZIP (geralmente o único)
        json_ = z.namelist()[0]

        with z.open(json_) as f:
            estabelecimentos = json.load(f)

    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(estabelecimentos, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved raw API response to {outpath}")


def main():
    """
    Download and process CNES establishments data from DATASUS JSON.
    If JSON exists, load it; otherwise, download and extract from ZIP.
    Then create a flat CSV from the JSON.
    """
    outpath = "data/CNES/estabelecimentos_cnes.json"

    print("Iniciando o processo de busca e criação da tabela de estabelecimentos do CNES...")

    # Colunas de interesse que vamos extrair do JSON original.

    try:
        # Verifica se o JSON já existe
        if os.path.exists(outpath):
            print(f"JSON já existe em {outpath}. Carregando...")
        else:
            _request(outpath)
            print(f"JSON baixado e salvo em {outpath}.")

        with open(outpath, "r", encoding="utf-8") as f:
            estabelecimentos = json.load(f)

        print("JSON carregado com sucesso. Transformando para CSV...")

        # Load JSON into pandas DataFrame
        df = pd.DataFrame(estabelecimentos)

        # Select only the columns of interest
        df_selected = df[CNES_COLUMNS]

        # Save to CSV
        csv_path = outpath.replace(".json", ".csv")
        df_selected.to_csv(csv_path, index=False, encoding="utf-8")

        print("✅ CSV criado")

    except requests.exceptions.RequestException as e:
        print(f"\nErro ao baixar o arquivo: {e}")

    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
