import subprocess
from xml.etree import ElementTree as ET
import os
from datetime import datetime
import glob
import csv

def install_and_import_pandas():
    try:
        import pandas as pd
        return pd
    except ImportError:
        print("Pandas não está instalado. Tentando instalar...")
        subprocess.run(["pip3", "install", "pandas"])
        import pandas as pd
        return pd

def extract_data_from_xml(file_path, keys, namespace):
    tree = ET.parse(file_path)
    root = tree.getroot()
    data_list = []

    common_data_dict = {}
    for key, alias in keys.items():
        if key not in ["xProd", "CFOP", "uCom", "qCom", "vProd"]:  # Skip item-specific keys
            element = root.find(f".//ns:{key}", namespaces=namespace)
            common_data_dict[alias] = element.text if element is not None else None

    for item in root.findall(".//ns:det", namespaces=namespace):
        item_data_dict = common_data_dict.copy()
        for key, alias in keys.items():
            if key in ["xProd", "CFOP", "uCom", "qCom", "vProd"]:
                element = item.find(f".//ns:{key}", namespaces=namespace)
                item_data_dict[alias] = element.text if element is not None else None
        data_list.append(item_data_dict)

    return data_list


def main(pd):
    keys = {
        "nNF": "Nota Fiscal",
        "dhEmi": "Data emissao",
        "xNome": "Nome empresa",
        "CFOP": "CFOP - Natureza de Operacao",
        "xProd": "Produto",
        "uCom": "UNID",
        "qCom": "Qtd Produto",
        "vProd": "Valor Produto",

    }
    namespace = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
    data_list = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    leitor_nota_fiscal_folder = script_dir
    notas_folder_path = os.path.join(leitor_nota_fiscal_folder, 'notas')

    for file_path in glob.glob(os.path.join(notas_folder_path, '*.xml')):
        data_dicts = extract_data_from_xml(file_path, keys, namespace)
        data_list.extend(data_dicts)

    df = pd.DataFrame(data_list)

    # Generate the CSV filename based on the current date and version number
    today = datetime.now().strftime('%Y_%m_%d')
    version = 1
    csv_filename = f"extracted_data_{today}_v{version}.csv"
    csv_path = os.path.join(leitor_nota_fiscal_folder, csv_filename)

    while os.path.exists(csv_path):
        version += 1
        csv_filename = f"extracted_data_{today}_v{version}.csv"
        csv_path = os.path.join(leitor_nota_fiscal_folder, csv_filename)

    df.to_csv(csv_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

if __name__ == "__main__":
    pd = install_and_import_pandas()
    if pd:
        main(pd)
    else:
        print("Não foi possível instalar ou importar o Pandas. O script não pode continuar.")
