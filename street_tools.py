from difflib import get_close_matches
import ast
import time # Para evaluar la string como diccionarios
from urllib import parse, request
import pandas as pd
import numpy as np

def alphanumerical_to_digit(street):
    "Checks if a number is in alphanumerical representation and changes to digits"

    str_to_number = {'PRIMERO':1,
                     'SEGUNDO':2,
                     'TRES':3,
                     'CUATRO':4,
                     'CINCO':5,
                     'SEIS':6,
                     'SIETE':7,
                     'OCHO':8,
                     'NUEVE':9,
                     'DIEZ':10,
                     'ONCE':11,
                     'DOCE':12,
                     'TRECE':13,
                     'CATORCE':14,
                     'QUINCE':15,
                     'DIECISEIS':16,
                     'DIECISIETE':17,
                     'DIECIOCHO':18,
                     'DIECINUEVE':19,
                     'VEINTE':20,
                     'VEINTIUNO':21,
                     'VEINTIDOS':22,
                     'VEINTITRES':23,
                     'VEINTICUATRO':24,
                     'VEINTICINCO':25,
                     'VEINTISEIS':26,
                     'VEINTISIETE':27,
                     'VEINTIOCHO':28,
                     'VEINTINUEVE':29,
                     'TREINTA':30,
                     'TREINTA Y UNO':31
                     }
    
    
    number = list(set(str_to_number.keys())&set(street.split()))
    
    if number:
        number = number[0]
        return street.replace(number,str(str_to_number.get(number)))
    else:
        return street


def digit_to_alphanumerical(street):
    "Checks if a number is in digits representation and changes to alphanumerical"
    
    number_to_string =  {'1': 'UNO',
                         '2': 'DOS',
                         '3': 'TRES',
                         '4': 'CUATRO',
                         '5': 'CINCO',
                         '6': 'SEIS',
                         '7': 'SIETE',
                         '8': 'OCHO',
                         '9': 'NUEVE',
                         '10': 'DIEZ',
                         '11': 'ONCE',
                         '12': 'DOCE',
                         '13': 'TRECE',
                         '14': 'CATORCE',
                         '15': 'QUINCE',
                         '16': 'DIECISEIS',
                         '17': 'DIECISIETE',
                         '18': 'DIECIOCHO',
                         '19': 'DIECINUEVE',
                         '20': 'VEINTE',
                         '21': 'VEINTIUNO',
                         '22': 'VEINTIDOS',
                         '23': 'VEINTITRES',
                         '24': 'VEINTICUATRO',
                         '25': 'VEINTICINCO',
                         '26': 'VEINTISEIS',
                         '27': 'VEINTISIETE',
                         '28': 'VEINTIOCHO',
                         '29': 'VEINTINUEVE',
                         '30': 'TREINTA',
                         '31': 'TREINTA Y UNO'}
    
    digit = list(set(number_to_string.keys())&set(street.split()))
    if digit:
        return street.replace(digit[0],str(number_to_string.get(digit[0])))



def suggest_dep(string):
    """Suggest a departamento """
    departamentos =(["artigas",
                     "canelones",
                     "cerro largo",
                     "colonia",
                     "durazno",
                     "flores",
                     "florida",
                     "lavalleja",
                     "maldonado",
                     "montevideo",
                     "paysandú",
                     "río negro",
                     "rivera",
                     "rocha",
                     "salto",
                     "san josé",
                     "soriano",
                     "tacuarembó",
                     "treinta y tres"])
    return get_close_matches(string.lower(),departamentos,n=2,cutoff=0.6)[0]



def process_street(street):
    """Processstreet information into INE format"""
    
    
    df = pd.read_excel('Consideraciones particulares.xlsx',header=2) #This is a file for a non coder user load special info in order to help processing data
    
    streets_with_digit = df[df.columns[0]].dropna().astype('str').to_list()
    
    aptos = df[df.columns[2]].dropna().astype('str').to_list()
    
    forbidden_char = df[df.columns[4]].dropna().astype('str').to_list()
    
    unnamed_streets =  df[df.columns[6]].dropna().astype('str').to_list()

    street = street.strip()

    try:
        street = street.upper()
    except:
        None
    
    for unnamed in unnamed_streets: #Search for char combinations meaning "no name" 
        if unnamed in street[:len(unnamed)]: 
            street = street.replace(unnamed,"")
            break 

    for apto in aptos:
        if apto in street:
            street = "".join(street.split(apto)[0])
    

    for char in forbidden_char:
        if char == "S/N" and char in street:
            if street.split().index("S/N") == len(street.split())-1:
                street = street.replace(char,"1")
            else:
                street = street.replace(char,"")
    if set(streets_with_digit)&set(street.split()):
        try:
            street, number = digit_to_alphanumerical(street)
        except:
            None
            
    
    try:
        if street.split()[-1].isdigit() and len(street.split())>1:
            number = street.split()[-1] # Gets the door number of the address, if fails asigns "1" as door number
            street = ' '.join(street.split()[:-1]) 
        else:
            number = "1"
    except:
            number = "1"
            
    return street, number


def suggest_streets(string,tryouts=3):
    """Suggest streets from data using IDE API"""
    query_args = {
        "entrada" : string, 
        "todos":False
    }
    root = 'https://direcciones.ide.uy/'
    URL = root + '/api/v0/geocode/SugerenciaCalleCompleta?'
    
    while tryouts > 0:
        try:
            r = request.urlopen(URL+parse.urlencode(query_args))
            data = r.read().decode('utf-8').replace('null','None')
            break
        except Exception as e:
            tryouts -= 1
            if tryouts == 0:
                return []
            time.sleep(0.25)
            
            
    if data=='[]': #Server returns no data
        return []
    else:
        return ast.literal_eval(data)

def suggest_location(localidad, departamento, limit=10, tryouts=3):
    """Suggest a location from a strings and checks if exists in the countys(departamento). Retunrs suggested location and id"""

    
    departamentos =(["artigas",
                    "canelones",
                    "cerro largo",
                    "colonia",
                    "durazno",
                    "flores",
                    "florida",
                    "lavalleja",
                    "maldonado",
                    "montevideo",
                    "paysandú",
                    "río negro",
                    "rivera",
                    "rocha",
                    "salto",
                    "san josé",
                    "soriano",
                    "tacuarembó",
                    "treinta y tres"])
    
    candidato_departamento = get_close_matches(departamento.lower(),departamentos,n=limit,cutoff=0.6)[0] 
    
    string = localidad + ", "+candidato_departamento
    
    query_args = {
        "limit": 10,
        "q" : string, 
        "soloLocalidad":True
    }
    
    
    root = 'https://direcciones.ide.uy/'
    URL = root + 'api/v1/geocode/candidates?'
    while tryouts > 0:

        try:
            r = request.urlopen(URL+parse.urlencode(query_args))
            break
        except Exception as e:
            tryouts -= 1
            if tryouts ==0:
                return {'error':e}
            time.sleep(0.5)
    
    data = r.read().decode('utf-8')
    
    if data=='[]':
        return {'error':'No existe localidad similar'}
    else:
        data = ast.literal_eval(data.replace('null','None')) 
    try:
        localidades = [x.get('address').lower().split(',')[0] for x in data]
        idlocalidades = [x.get('idLocalidad') for x in data]
        loc_suggested = get_close_matches(localidad.lower(),localidades,n=limit,cutoff=0.6)[0] #Para localidad el matcheo queda en 0.6
        idloc_suggested = idlocalidades[localidades.index(loc_suggested)]
        return [loc_suggested , idloc_suggested]
    except Exception as e:
        loc_suggested = " "
        idloc_suggested = " "
        return [loc_suggested , idloc_suggested]


def search_from_API(street, loc, dep):
    
    """Finds a direction given a location and a street. Returns a dictionary with street info. """
    
    
    if street and street.isdigit():
        street += " " + street # INE API searchs "only numbers" by duplication, ex:  "60 60" is a valid entry for "calle 60"

    suggestions = suggest_streets(street)  
    
    try:
        street = str(street) 
    except Exception as e:
        return {'error':'La calle no contiene string'} 
    
    dep = dep.strip()
    
    if not suggestions: 
        return  {'error':'No se encuentra calle simular'}
    
    
    streets = [x.get('calle').lower() for x in suggestions] # Hay que trabajar con lower dado que las mayusculas afectan el ratio
    suggested_loc = [x.get('localidad').lower() for x in suggestions if x.get('localidad') is not None]
    suggested_idstreet = [x.get('idCalle') for x in suggestions] 
    suggested_idloc = [x.get('idLocalidad') for x in suggestions if x.get('idLocalidad') is not None] 
    suggested_dep = [x.get('departamento').lower() for x in suggestions if x.get('departamento') is not None] 
    
    
    suggested_streets = get_close_matches(street.lower(),street,n=14,cutoff=0.6) 
    
    try:
        loc, idloc = suggest_location(loc.lower(),dep)
    except:
        return {'error':'error al sugerir localidad'}
    if not loc:
        return {'error':"no se encuentra localidad"}

    
    suggested_street_indexes = [x for x in range(len(suggested_loc)) if suggested_loc[x] == loc]
    suggested_streets = [streets[x] for x in suggested_street_indexes]
    suggested_idstreet = [suggested_idstreet[x] for x in suggested_street_indexes]
    suggested_dep =  [suggested_dep[x] for x in suggested_street_indexes]
    suggested_idloc = [suggested_idloc[x] for x in suggested_street_indexes]

    if not suggested_streets:
        return {'error':'No se encuentra calle similar'}
    
    if suggested_streets.count(suggested_streets[0])> 1:
        return {'error':'Calle Duplicada'}
    
    else:
        try:
            result = ({'calle':suggested_streets[0], #Returns the best match
                   'id':suggested_idstreet[0],
                   'localidad':loc,
                   'idlocalidad':idloc,
                   'departamento':suggested_dep[0],
                   'fuente':'API INE'})
            return result
        except Exception as e:
            return {'error':e}

def search_from_frame(street, loc, dep, df):
    "Search street data in the Dataframe"
    dep = dep.upper()    #Dataframe data is in upper
    loc = loc.upper()
    
    
    try:
        suggested_dep = get_close_matches(dep,df.departamento.unique(),n=14,cutoff=0.6)[0] #Finds best match
    except Exception as e:
        return {'error':'No se encuentra departamento en el frame'}
    try:
        suggested_loc = get_close_matches(loc,df[df['departamento']==suggested_dep]['localidad'].unique(),n=14,cutoff=0.8)[0]
        
    except Exception as e:
        return {'error':'No encuentro localidad en el nomenclator'} 
    
    try:
        suggested_street = get_close_matches(street,df[(df['departamento']==suggested_dep)&(df['localidad']==suggested_loc)]['calle'].unique(),n=10,cutoff=0.6)[0]
    except Exception as e:
        try: #When edit distance fails to get a result words are counted, the candidate with the most common with data is returned
            candidates = df[(df['departamento']==suggested_dep)&(df['localidad']==suggested_loc)]['calle'].unique()
            word_counts = [count_matches(street,candidate) for candidate in candidates]
            if sum(word_counts) == 0:
                return {'error': 'No se encuentra dirección ingresada'}
            suggested_street = candidates[np.argmax(word_counts)]
        except:
            return {'error': 'No se encuentra dirección ingresada'}
        
    try:
        _ , idloc = suggest_location(suggested_loc,suggested_dep,limit=10)
        if len((df[(df['departamento']==suggested_dep)
                   &(df['calle']==suggested_street)
                   &(df['localidad']==suggested_loc)]['idcalle'])) > 1:
            return {'error':'Calle duplicada'}
        
        result = ({'calle':suggested_street , #Returns match
                   'id': (int(df[(df['departamento']==suggested_dep)
                                 &(df['calle']==suggested_street)
                                 &(df['localidad']==suggested_loc)]['idcalle'])),
                   'localidad':suggested_loc,
                   'idlocalidad':idloc,
                   'departamento':suggested_dep,
                   'fuente':'Codificador'})
        return result
    except Exception as e:
        return {'error': 'No encuentro localidad en el nomenclator'}


def get_data_IDE(street, loc, dep, df):
    """ Searchs for street data in INE API and/or INE DataFrame"""    
    
    error = "" #DEFAULT ERROR
    
    special_charecters = [",", "-"]
    exceptional_locs = ['PINEPARK', 'LAS DELICIAS', "ESTACION"] #Exceptions of locations in the Nomenclator, ex: "PINAMAR - PINEPARK"
    
    possible_locs = []
    

    
    if not street: 
        return {'error':'No se encuentra dirección ingresada'}
    
    
    for char in special_charecters: 
        if set(exceptional_locs)&set(loc): 
            break
        if char in loc:
            possible_locs = loc.split(char)
            break
    
    if isinstance(loc,str) :
        possible_locs.append(loc)
    else:
        possible_locs = [x.strip().upper() for x in possible_locs]


    ### ---------------If dep is empty suggest one---------------------------
        
    if not dep:
        for loc in possible_locs:
            dep = suggest_dep(loc)
            if dep:
                possible_locs.pop(possible_locs.index(loc))
                break
                
    if street.split()[0].isdigit() and len(street.split()) > 1:
        
        for loc in possible_locs:
            result = search_from_frame(street,loc,dep,df)
            if 'error' not in result.keys():
                return result
            else:
                if not street:
                    return {'error':"No se encuentra dirección ingresada"}
                street = digit_to_alphanumerical(street)
        
    ### -------------------------------------------------------------------------- 


    for loc in possible_locs:
        result = search_from_API(street,loc,dep)
        if not 'error' in result.keys():
            return result
      
        else:
            if not error:
                error = ' '.join((error, result.get('error')))
            else:
                error = result.get('error')
            
            result = search_from_frame(street, loc, dep, df)
            
            if 'error' in result.keys():
                error = result.get('error')
                return {'error':error}
            
    return result

def search_street(street, loc, dep, df): 
    """Calls get_data_INE for data of a street. 
    If it fails it changes the street name to fix INE notation problems (mostly dates) and tries again. 
    """
    result = get_data_IDE(street, loc, dep, df)
    if 'error' in result.keys() and street.split()[0] == "CALLE":
        street = street.replace("CALLE","")
        result = get_data_IDE(street, loc, dep, df)
    return result

def search_address(street, loc, dep, codificador, tryouts=3):
    """Finds a location """

    street = parse.unquote(street)
    
    street, number = process_street(street)
    
    validated_street = search_street(street, loc, dep, codificador)
    street = validated_street.get('calle')
        
    if not street or  validated_street.get("error") == 'Calle duplicada':
        return ({'calleNormalizada':'',
                 'idCalleIDE':'',
                 'nro_puerta':'',
                 'codigoPostal':'',
                 'puntoX':'',
                 'puntoY':'',
                 'idPuntoIDE':'',
                 'error':validated_street.get('error')})
    
    street = street + ' ' + number + ' '
    dep = dep.upper() + ' '
    loc = loc.upper()

    root = 'https://direcciones.ide.uy/'
    URL = root + 'api/v0/geocode/BusquedaDireccion?'
    
    query_args = {
        "calle" : street, 
        "departamento":dep,
        "localidad":loc
    }
    
    while tryouts > 0:
        try:
            r = request.urlopen(URL+parse.urlencode(query_args, quote_via=parse.quote))
            data = r.read().decode('utf-8').replace('null', 'None')
            break
        except Exception as e:
            tryouts -= 1
            if tryouts == 0:
                return ({'calleNormalizada':'',
                         'idCalleIDE':'',
                         'nro_puerta':'',
                         'codigoPostal':'',
                         'puntoX':'',
                         'puntoY':'',
                         'idPuntoIDE':'',
                         'error': str(e) + ' en API IDE'})
            
    result = ast.literal_eval(data)

    for parcial in result:
        dire = parcial.get('direccion')
        try:
            street_id = dire.get('calle').get('idCalle')
        except Exception as e:
            return ({'calleNormalizada':'',
                     'idCalleIDE':'',
                     'nro_puerta':'',
                     'codigoPostal':'',
                     'puntoX':'',
                     'puntoY':'',
                     'idPuntoIDE':'',
                     'error':'No se encuentra dirección ingresada'})

        if street_id == validated_street.get('id'):
            result = parcial
            break
        result = []

    if isinstance(result, list):
        return ({'calleNormalizada':'',
                 'idCalleIDE':'',
                 'nro_puerta':'',
                 'codigoPostal':'',
                 'puntoX':'',
                 'puntoY':'',
                 'idPuntoIDE':'',
                 'error':'No se encuentra dirección ingresada'})

            
    if result:
        calle_nor = result.get('direccion').get('calle').get('nombre_normalizado')
        calle_id = result.get('direccion').get('calle').get('idCalle')
        nro_puerta = result.get('direccion').get('numero', {'nro_puerta':'1'}).get('nro_puerta') 
        codigo_Postal = result.get('codigoPostal')
        punto_X = result.get('puntoX')
        punto_Y = result.get('puntoY')
        id_Punto_IDE = result.get('idPunto')
        error = ""

        return ({'calleNormalizada':calle_nor,
                 'idCalleIDE':calle_id,
                 'nro_puerta_aprox':nro_puerta,
                 'codigoPostal':codigo_Postal,
                 'puntoX':punto_X,
                 'puntoY':punto_Y,
                 'idPuntoIDE':id_Punto_IDE,
                 'error':error})
    
    elif street.split()[0].isdigit():  #Changes streets that made from numbers, like '3'
        street = digit_to_alphanumerical(street) 

        return search_address(street, loc, dep, codificador)
    else:
        
        return ({'calleNormalizada':'',
                 'idCalleIDE':'',
                 'nro_puerta':'',
                 'codigoPostal':'',
                 'puntoX':'',
                 'puntoY':'',
                 'idPuntoIDE':'',
                 'error':'No se encuentra dirección ingresada'})


