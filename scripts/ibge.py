import json
import os

import requests
from tqdm import tqdm

IBGE_API = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


def _request(outpath: str = "data/ibge/municipalities.json"):
    response = requests.get(IBGE_API, timeout=30)
    response.raise_for_status()

    municipalities = response.json()

    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(municipalities, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved raw API response to {outpath}")


def main(json_path: str = "data/ibge/municipalities.json", csv_path: str = "data/ibge/municipalities_flat.csv"):
    print("🌐 Fetching municipality data from IBGE API...")
    if not os.path.exists(json_path):
        _request(outpath=json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        municipalities: list[dict] = json.load(f)

    with open(csv_path, "w", encoding="utf-8") as f:
        header = "id,nome,microrregiao_id,microrregiao_nome,mesorregiao_id,mesorregiao_nome,uf_id,uf_sigla,uf_nome,regiao_id,regiao_sigla,regiao_nome,regiao_imediata_id,regiao_imediata_nome,regiao_intermediaria_id,regiao_intermediaria_nome\n"
        f.write(header)

        runner = tqdm(municipalities, total=len(municipalities), desc="Processing municipalities", unit="mun")
        for m in municipalities:
            runner.desc = f"Processing {m['nome']}"

            micro: dict = m.get("microrregiao", {})
            if not isinstance(micro, dict):
                micro = {}

            meso: dict = micro.get("mesorregiao", {})
            uf: dict = meso.get("UF", {})
            regiao_imediata: dict = m.get("regiao-imediata", {})
            regiao_intermediaria: dict = regiao_imediata.get("regiao-intermediaria", {})

            row = [
                str(m.get("id", "")),
                m.get("nome", ""),
                str(micro.get("id", "")),
                micro.get("nome", ""),
                str(meso.get("id", "")),
                meso.get("nome", ""),
                str(uf.get("id", "")),
                uf.get("sigla", ""),
                uf.get("nome", ""),
                str(uf.get("regiao", {}).get("id", "")),
                uf.get("regiao", {}).get("sigla", ""),
                uf.get("regiao", {}).get("nome", ""),
                str(regiao_imediata.get("id", "")),
                regiao_imediata.get("nome", ""),
                str(regiao_intermediaria.get("id", "")),
                regiao_intermediaria.get("nome", ""),
            ]
            f.write(",".join(row) + "\n")
            runner.update(1)

        runner.close()

        print(f"✅ Transformed JSON data to flat CSV at {csv_path}")


if __name__ == "__main__":
    main()
