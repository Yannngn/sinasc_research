import json
from pathlib import Path

SOURCE = "https://opendatasus.saude.gov.br/dataset/sistema-de-informacao-sobre-nascidos-vivos-sinasc/resource/883f5df5-4bb3-46d3-a1f8-f5834f9cc2a3?inner_span=True"

PATH = "data/SINASC"

SINASC_COLUMNS = {
    # Core fields (from 1996)
    "CONTADOR": "Int32",  # Número identificador do registro - sequence counter
    "LOCNASC": "category",  # Local nascimento (1-5, 9)
    "CODMUNNASC": "string",  # Código IBGE município nascimento
    "IDADEMAE": "Int8",  # Idade da mãe
    "ESTCIVMAE": "category",  # Estado civil (1-5, 9)
    "ESCMAE": "category",  # Escolaridade (1-5, 9)
    "CODOCUPMAE": "string",  # Ocupação mãe (CBO)
    "QTDFILVIVO": "Int8",  # Filhos vivos
    "QTDFILMORT": "Int8",  # Perdas fetais e abortos
    "CODMUNRES": "string",  # Código IBGE município residência
    "GESTACAO": "category",  # Semanas gestação (1-6, 9)
    "GRAVIDEZ": "category",  # Tipo gravidez (1-3, 9)
    "PARTO": "category",  # Tipo parto (1-2, 9)
    "CONSULTAS": "category",  # Consultas pré-natal (1-4, 9)
    "DTNASC": "date",  # Data nascimento (ddmmaaaa)
    "SEXO": "category",  # Sexo (0-2)
    "APGAR1": "Int8",  # Apgar 1º minuto (0-10)
    "APGAR5": "Int8",  # Apgar 5º minuto (0-10)
    "RACACOR": "category",  # Raça/Cor (1-5)
    "PESO": "Int16",  # Peso em gramas
    "CODANOMAL": "string",  # Código anomalia (CID-10)
    # Added in 1997
    "HORANASC": "time",  # Horário nascimento
    "IDANOMAL": "category",  # Anomalia congênita (1-2, 9)
    # Added in 2000
    "CODESTAB": "string",  # Código estabelecimento CNES
    "UFINFORM": "string",  # UF informante
    # Added in 2006
    "DTCADASTRO": "date",  # Data cadastramento
    "DTRECEBIM": "date",  # Data recebimento
    # Added in 2010
    "ORIGEM": "category",  # Origem dados (1-3)
    "CODCART": "string",  # Código cartório
    "NUMREGCART": "string",  # Número registro cartório
    "DTREGCART": "date",  # Data registro cartório
    "CODPAISRES": "string",  # Código país residência
    "NUMEROLOTE": "string",  # Número lote
    "VERSAOSIST": "string",  # Versão sistema
    "DIFDATA": "Int16",  # Diferença datas ([DTNASC] – [DTRECORIGA])
    "DTRECORIG": "date",  # Data primeiro recebimento
    "NATURALMAE": "string",  # Naturalidade mãe
    "CODMUNNATU": "string",  # Código município naturalidade mãe
    "SERIESCMAE": "category",  # Série escolar mãe (1-8)
    "DTNASCMAE": "date",  # Data nascimento mãe
    "RACACORMAE": "category",  # Raça/cor mãe
    "QTDGESTANT": "Int8",  # Gestações anteriores
    "QTDPARTNOR": "Int8",  # Partos vaginais
    "QTDPARTCES": "Int8",  # Partos cesáreos
    "IDADEPAI": "Int8",  # Idade pai
    "DTULTMENST": "date",  # Data última menstruação
    "SEMAGESTAC": "Int8",  # Semanas gestação calculadas
    "TPMETESTIM": "category",  # Método estimação (1-2, 9)
    "CONSPRENAT": "Int8",  # Consultas pré-natal (número)
    "MESPRENAT": "Int8",  # Mês início pré-natal
    "TPAPRESENT": "category",  # Apresentação RN (1-3, 9)
    "STTRABPART": "category",  # Trabalho parto induzido (1-3, 9)
    "STCESPARTO": "category",  # Cesárea antes trabalho parto (1-3, 9)
    "TPROBSON": "category",  # Grupo Robson
    "STDNEPIDEM": "bool",  # Status epidemiológico (0-1)
    "STDNNOVA": "bool",  # Status nova (0-1)
    # Added in 2011-2012
    "RACACOR_RN": "category",  # Raça/cor RN (deprecated)
    "RACACORN": "category",  # Raça/cor RN (1-5)
    "ESCMAE2010": "category",  # Escolaridade 2010 (0-5, 9)
    # Added in 2013
    "CODMUNCART": "string",  # Código município cartório
    "CODUFNATU": "string",  # UF naturalidade
    "TPNASCASSI": "category",  # Nascimento assistido por (1-4, 9)
    "ESCMAEAGR1": "category",  # Escolaridade agregada (0-12)
    # Added in 2014
    "DTRECORIGA": "date",  # Data recebimento original
    "TPFUNCRESP": "category",  # Função responsável (1-5)
    "TPDOCRESP": "category",  # Documento responsável (1-5)
    "DTDECLARAC": "date",  # Data declaração
    "PARIDADE": "bool",  # Paridade (0-1)
    "KOTELCHUCK": "category",  # Índice Kotelchuck
    "OPORT_DN": "Int16",  # Diferença entre Data de Registro Oportuno e data de nascimento (?)
}

VALUE_MAPPINGS = {
    "LOCNASC": {1: "Hospital", 2: "Outros estabelecimentos de saúde", 3: "Domicílio", 4: "Outros", 5: "Aldeia Indígena", 9: "Ignorado"},
    "ESTCIVMAE": {1: "Solteira", 2: "Casada", 3: "Viúva", 4: "Separada judicialmente/divorciada", 5: "União estável", 9: "Ignorada"},
    "ESCMAE": {1: "Nenhuma", 2: "1 a 3 anos", 3: "4 a 7 anos", 4: "8 a 11 anos", 5: "12 e mais", 9: "Ignorado"},
    "GESTACAO": {
        1: "Menos de 22 semanas",
        2: "22 a 27 semanas",
        3: "28 a 31 semanas",
        4: "32 a 36 semanas",
        5: "37 a 41 semanas",
        6: "42 semanas e mais",
        9: "Ignorado",
    },
    "GRAVIDEZ": {1: "Única", 2: "Dupla", 3: "Tripla ou mais", 9: "Ignorado"},
    "PARTO": {1: "Vaginal", 2: "Cesário", 9: "Ignorado"},
    "CONSULTAS": {1: "Nenhuma", 2: "de 1 a 3", 3: "de 4 a 6", 4: "7 e mais", 9: "Ignorado"},
    "SEXO": {0: "Ignorado", 1: "Masculino", 2: "Feminino"},
    "RACACOR": {1: "Branca", 2: "Preta", 3: "Amarela", 4: "Parda", 5: "Indígena"},
    "RACACORMAE": {1: "Branca", 2: "Preta", 3: "Amarela", 4: "Parda", 5: "Indígena"},
    "RACACORN": {1: "Branca", 2: "Preta", 3: "Amarela", 4: "Parda", 5: "Indígena"},
    "IDANOMAL": {1: "Sim", 2: "Não", 9: "Ignorado"},
    "ORIGEM": {1: "Oracle", 2: "FTP", 3: "SEAD"},
    "ESCMAE2010": {
        0: "Sem escolaridade",
        1: "Fundamental I (1ª a 4ª série)",
        2: "Fundamental II (5ª a 8ª série)",
        3: "Médio (antigo 2º Grau)",
        4: "Superior incompleto",
        5: "Superior completo",
        9: "Ignorado",
    },
    "TPMETESTIM": {1: "Exame físico", 2: "Outro método", 9: "Ignorado"},
    "TPAPRESENT": {1: "Cefálico", 2: "Pélvica ou podálica", 3: "Transversa", 9: "Ignorado"},
    "STTRABPART": {1: "Sim", 2: "Não", 3: "Não se aplica", 9: "Ignorado"},
    "STCESPARTO": {1: "Sim", 2: "Não", 3: "Não se aplica", 9: "Ignorado"},
    "TPNASCASSI": {1: "Médico", 2: "Enfermagem ou Obstetriz", 3: "Parteira", 4: "Outros", 9: "Ignorado"},
    "ESCMAEAGR1": {
        0: "Sem Escolaridade",
        1: "Fundamental I Incompleto",
        2: "Fundamental I Completo",
        3: "Fundamental II Incompleto",
        4: "Fundamental II Completo",
        5: "Ensino Médio Incompleto",
        6: "Ensino Médio Completo",
        7: "Superior Incompleto",
        8: "Superior Completo",
        9: "Ignorado",
        10: "Fundamental I Incompleto ou Inespecífico",
        11: "Fundamental II Incompleto ou Inespecífico",
        12: "Ensino Médio Incompleto ou Inespecífico",
    },
    "TPFUNCRESP": {1: "Médico", 2: "Enfermeiro", 3: "Parteira", 4: "Funcionário do cartório", 5: "Outros"},
    "TPDOCRESP": {1: "CNES", 2: "CRM", 3: "COREN", 4: "RG", 5: "CPF"},
    "STDNEPIDEM": {0: "Não", 1: "Sim"},
    "STDNNOVA": {0: "Não", 1: "Sim"},
    "PARIDADE": {0: "Nulípara", 1: "Multípara"},
    "KOTELCHUCK": {1: "Inadequado", 2: "Intermediário", 3: "Adequado", 4: "Mais que adequado"},
}

COLUMN_RENAME_MAPPING = {
    # Core fields (from 1996)
    "CONTADOR": "index",
    "LOCNASC": "birth_location_type",  # category
    "CODMUNNASC": "birth_municipality_code",  # code
    "IDADEMAE": "mother_age",  # int
    "ESTCIVMAE": "mother_marital_status",  # category
    "ESCMAE": "mother_education_category",  # category
    "CODOCUPMAE": "mother_occupation_code",  # code
    "QTDFILVIVO": "living_children_count",  # int
    "QTDFILMORT": "deceased_children_count",  # int
    "CODMUNRES": "residence_municipality_code",  # code
    "GESTACAO": "term_category",  # category
    "GRAVIDEZ": "pregnancy_type",  # category
    "PARTO": "delivery_type",  # category
    "CONSULTAS": "prenatal_consultations_category",  # category
    "DTNASC": "birth_date",  # date
    "SEXO": "sex_category",  # category
    "APGAR1": "apgar_score_1min_int",  # int
    "APGAR5": "apgar_score_5min_int",  # int
    "RACACOR": "race_category",  # category
    "PESO": "birth_weight_grams",  # int
    "CODANOMAL": "anomaly_code",  # code
    # Added in 1997
    "HORANASC": "birth_time",  # time (transform to int HH * 60 + MM)
    "IDANOMAL": "has_congenital_anomaly_category",  # category
    # Added in 2000
    "CODESTAB": "establishment_code",  # code
    "UFINFORM": "registry_office_state_code",  # code
    # Added in 2006
    "DTCADASTRO": "registration_date",  # date
    "DTRECEBIM": "registration_received_date",  # date
    # Added in 2010
    "ORIGEM": "data_origin_category",  # category
    "CODCART": "registry_office_code",  # code
    "NUMREGCART": "registry_office_code",  # code
    "DTREGCART": "registry_office_registration_date",  # date
    "CODPAISRES": "residence_country_code",  # code
    "NUMEROLOTE": "batch_code",  # code
    "VERSAOSIST": "system_version_code",  # code
    "DIFDATA": "birth_registry_office_registration_date_difference_days",  # int
    "DTRECORIG": "original_received_date",  # date
    "NATURALMAE": "mother_birthplace",  # string
    "CODMUNNATU": "mother_birthplace_municipality_code",  # code
    "SERIESCMAE": "mother_school_grade_category",  # category
    "DTNASCMAE": "mother_birth_date",  # date
    "RACACORMAE": "mother_race_category",  # category
    "QTDGESTANT": "previous_pregnancies_count",  # int
    "QTDPARTNOR": "normal_deliveries_count",  # int
    "QTDPARTCES": "cesarean_deliveries_count",  # int
    "IDADEPAI": "father_age",  # int
    "DTULTMENST": "last_menstruation_date",  # date
    "SEMAGESTAC": "gestational_weeks_count",  # int
    "TPMETESTIM": "gestational_age_estimation_method_category",  # category
    "CONSPRENAT": "prenatal_consultations_count",  # int
    "MESPRENAT": "prenatal_care_start_month",  # int
    "TPAPRESENT": "fetal_presentation_type",  # category
    "STTRABPART": "labor_induced_status",  # category
    "STCESPARTO": "cesarean_before_labor_status",  # category
    "TPROBSON": "robson_classification_type",  # category
    "STDNEPIDEM": "epidemiological_status",  # category
    "STDNNOVA": "new_status",  # category
    # Added in 2011-2012
    "RACACOR_RN": "race_color_rn_1_deprecated",  # deprecated
    "RACACORN": "race_color_rn_2_deprecated",  # deprecated
    "ESCMAE2010": "mother_education_deprecated",  # deprecated
    # Added in 2013
    "CODMUNCART": "registry_municipality_code",  # code
    "CODUFNATU": "mother_birthplace_state_code",  # code
    "TPNASCASSI": "birth_attendant_type",  # category
    "ESCMAEAGR1": "mother_education_complete_category",  # category
    # Added in 2014
    "DTRECORIGA": "processed_received_date",  # date
    "TPFUNCRESP": "responsible_professional_type",  # category
    "TPDOCRESP": "responsible_document_type",  # category
    "DTDECLARAC": "declaration_date",  # date
    "PARIDADE": "parity_category",  # category
    "KOTELCHUCK": "kotelchuck_category",  # category
    # Non-schema columns that might appear in actual data
    "OPORT_DN": "birth_opportunity_date_difference_days",  # int unknown but appears in data
}

with open(Path(PATH, "dtypes.json"), "w") as f:
    json.dump(SINASC_COLUMNS, f, indent=4, ensure_ascii=False)

with open(Path(PATH, "categorical.json"), "w") as f:
    json.dump(VALUE_MAPPINGS, f, indent=4, ensure_ascii=False)

with open(Path(PATH, "rename_mapping.json"), "w") as f:
    json.dump(COLUMN_RENAME_MAPPING, f, indent=4, ensure_ascii=False)
