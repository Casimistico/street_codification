import io
import json
import hug
import street_tools
import pandas as pd
import tempfile

@hug.get('/search_address_by_batch',output=hug.output_format.text,
         response_headers={'Content-Disposition': 'attachment; filename=result.txt'})


def search_addresses_by_batch(input_file):

    # Ajustar para aceptar un archivo
    """ 
    Get street data by batch
    """

    # <body> is a simple dictionary of {filename: b'content'}

    
    codificador = pd.read_csv('./Nomenclator/Nomenclator_calles.csv')

    
    file_desc, file_path = tempfile.mkstemp()
    #with open('prueba.txt','r',encoding='utf8') as input_file:
    with open(file_desc, "w",encoding='utf8') as tmp_file:
        for line in input_file:
            street, loc, dep = line.split(";")
            searched_data = (street_tools.search_address(street,loc,dep,codificador))
            tmp_file.write(json.dumps(searched_data))
            tmp_file.write('\n')
        tmp_file.close()
        input_file.close()
    f = open(file_path, 'rb')
    return f

    
@hug.get('/search_address')

def search_address(street:hug.types.text,
           loc:hug.types.text,
           dep:hug.types.text,
           ):
    """ 
    Get street data
    """
    codificador = pd.read_csv('./Nomenclator/Nomenclator_calles.csv')
    searched_data = (street_tools.search_address(street,loc,dep,codificador))

    return {"data":searched_data}
