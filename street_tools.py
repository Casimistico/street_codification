import pandas as pd
from difflib import SequenceMatcher, get_close_matches
import json, glob, re, time, ast # Para evaluar la string como diccionarios
from urllib import parse , request
from datetime import datetime
import numpy as np
from IPython.display import HTML, display, Image
import tabulate
import re


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
    """Process the street information into INE format"""
    
    #print("ENTRADA PROCESS STREET",street)
    forbidden_char = ["Nº", "S/N",",","."] #Remplaza caracteres que estorban en la busqueda
    non_street = [999] #Codigos para marcar que no es una calle
    streets_with_digit = ["SENDA","CALLE"]  
    # Arregla las calles "SIN NOMBRE". SI S/N Vuelve a aparecer mas adelante es "SIN NUMERO"
    aptos = ["APTO", "APARTAMENTO"]
    
    for apto in aptos:
        if apto in street:
            street = "".join(street.split(apto)[0])
    if street in non_street: 
        return "",""
    
    #try:
     #   street = street # Se fija si la calle contiene texto, Si es la calle es un numero lo devuelve como string
    #except: 
     #   return str(street) , "" #LA API de IDE acepta las calles con numero en formato str(numero)   str(numero) 
        
    for char in forbidden_char:
        street = street.replace(char,"1")
        
    if set(streets_with_digit)&set(street.split()):
        try:
            street, number = digit_to_alphanumerical(street)
        except:
            None
    try:
        if street.split()[-1].isdigit():
            number = street.split()[-1]
            street = ' '.join(street.split()[:-1])
        else:
            number = "1"
    except:
            number = "1"
    #print("SALIDA DE PROCESS STREET",street)
    return street, number

def suggest_streets(string,tryouts=3):
    """Sugiere calles a partir de una string"""
    query_args = {
        "entrada" : string, # La sugerencia a buscar
        "todos":False
    }
    root = 'https://direcciones.ide.uy/'
    URL = root + '/api/v0/geocode/SugerenciaCalleCompleta?'
    #r = request.Request(
    #        url=URL,
    #        data=parse.urlencode(query_args).encode('utf-8'),
    #    )
    
    while tryouts>0:
        try:
            r = request.urlopen(URL+parse.urlencode(query_args))
            data = r.read().decode('utf-8').replace('null','None')
            break
        except Exception as e:
            tryouts -= 1
            if tryouts == 0:
                return []
            time.sleep(0.5)
            
            
    if data=='[]':
        
        #print('No existe calle similar')
        return []
    else:
        return ast.literal_eval(data)

def suggest_location(localidad,departamento,limit=10,tryouts=3):
    """Sugiere una localidad a partir de una string y checkea contra un departamento devolviendo sugerencia e id"""

    
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
        "q" : string, # La sugerencia a buscar
        "soloLocalidad":True
    }
    
    
    root = 'https://direcciones.ide.uy/'
    URL = root + 'api/v1/geocode/candidates?'
    while tryouts>0:
        #r = request.Request(
        #        url=URL,
        #        data=parse.urlencode(query_args).encode('utf-8'),
        #    )
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
        #print("Este erro",e)
        loc_suggested = " "
        idloc_suggested = " "
        return [loc_suggested , idloc_suggested]

def search_from_API(street,loc,dep,warning=False):  #Mejorar la funcion si no tiene localidad
    """Encuentra una localidad dada una calle sugerida y una localidad. Devuelve un diccionario con los datos de esa calle"""
    
    #street, number = process_street(street)
    
    if street and street.isdigit():
        street += " " + street # La API busca los numeros de esta forma, ej: "60 60" es una busqueda valida para la calle 60
    suggestions = suggest_streets(street)  #Consulta por calles similares a la API IDE
    
    #print(suggestions)
    try:
        street = str(street) #Transformo las calles de numeros en strings #transformo las 
    except Exception as e:
        return {'error':'La calle no contiene string'}
    
    street = street.strip()   #Quito los espacios en blanco
    dep = dep.strip()
    if not suggestions: #Si no se devuelven calles similares
        return  {'error':'No se encuentra calle simular'}
    
    streets = [x.get('calle').lower() for x in suggestions] # Hay que trabajar con lower dado que las mayusculas afectan el ratio
    suggested_loc = [x.get('localidad').lower() for x in suggestions if x.get('localidad') is not None]
    suggested_idstreet = [x.get('idCalle') for x in suggestions] 
    suggested_idloc = [x.get('idLocalidad') for x in suggestions if x.get('idLocalidad') is not None] 
    suggested_dep = [x.get('departamento').lower() for x in suggestions if x.get('departamento') is not None] 
    #print(streets)
    suggested_streets = get_close_matches(street.lower(),street,n=14,cutoff=0.6) 
    #print(street, suggested_streets)
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
    #print(suggested_streets)
    if not suggested_streets:
        return {'error':'No se encuentra calle similar'}
    else:
        try:
            result = ({'calle':suggested_streets[0], #Solo se informa el primero
                       #'numero': number,
                   'id':suggested_idstreet[0],
                   'localidad':loc,
                   'idlocalidad':idloc,
                   'departamento':suggested_dep[0],
                   'fuente':'API INE'})
            return result
        except Exception as e:
            return {'error':e}

def search_from_frame(street,loc,dep,df):
    "Hace una busqueda en en cascada dep/loc/calle devolviendo un diccionario de datos"
    dep = dep    #Pasa a mayusculas ya que esta asi en el DF 
    loc = loc
    
    #street, number = process_street(street)
    try:
        suggested_dep = get_close_matches(dep,df.departamento.unique(),n=14,cutoff=0.6)[0] #Prueba buscar el departamento
    except: 
        return {'error':'No se encuentra departamento en el frame'}
    try:
        suggested_loc = get_close_matches(loc,df[df['departamento']==suggested_dep]['localidad'].unique(),n=14,cutoff=0.8)[0]
        
    except Exception as e:
        return {'error':'No encuentro localidad en el nomenclator'} 
    try:
        suggested_street = get_close_matches(street,df[(df['departamento']==suggested_dep)&(df['localidad']==suggested_loc)]['calle'].unique(),n=10,cutoff=0.6)[0]
    except Exception as e:
        try: #Si la distancia de edición no funciona cuento cuantas veces aparecen los nombres de las palabras dentro de la calle en los candidatos. Quien tiene más palabras gana
            candidates = df[(df['departamento']==suggested_dep)&(df['localidad']==suggested_loc)]['calle'].unique()
            word_counts = [count_matches(street,candidate) for candidate in candidates]
            if sum(word_counts) == 0:
                return {'error': 'No se encuentran los datos ingresados'}
            suggested_street = candidates[np.argmax(word_counts)]
        except:
            return {'error': 'No se encuentran los datos ingresados'}
        
    try:
        _ , idloc = suggest_location(suggested_loc,suggested_dep,limit=10)
        if len(df[(df['departamento']==suggested_dep)&(df['calle']==suggested_street)&(df['localidad']==suggested_loc)]['idcalle']) > 1:
            return {'error':'Calle duplicada'}
        
        result = ({'calle':suggested_street , #Solo se informa el primero
                   'numero': number,
                   'id': int(df[(df['departamento']==suggested_dep)&(df['calle']==suggested_street)&(df['localidad']==suggested_loc)]['idcalle']),
                   'localidad':suggested_loc,
                   'idlocalidad':idloc,
                   'departamento':suggested_dep,
                   'fuente':'Codificador'})
        return result
    except:
        return {'error': 'No se encuentran los datos ingresados'}

def get_data_IDE(street,loc,dep,df):
    """ Searchs for street data in INE API and/or INE DataFrame"""
    # HAY QUE ARREGLAR EL ULTIMO RETURN, esta en MODO DEBUG 
    
    error = ""
    # ----------
    
    special_charecters = [",","-"]
    possible_locs = []
    
    
    
    for char in special_charecters: #Search for only one of this characters. 
        if char in loc:
            possible_locs = loc.split(char)
            break
    
    if isinstance(loc,str) :
        possible_locs.append(loc)
    else:
        possible_locs = [x.strip().upper() for x in possible_locs]
        
    if not dep:
        for loc in possible_locs:
            dep = suggest_dep(loc)
            if dep:
                possible_locs.pop(possible_locs.index(loc))
                break
    
        
    if street.split()[0].isdigit():
        for loc in possible_locs:
            result = search_from_frame(street,loc,dep,df)
            if 'error' not in result.keys():
                return result
            else:
                street = digit_to_alphanumerical(street)
        
    #street = digit_to_alphanumerical(street) ### Reemplaza numeros de fechas letra a alfanumerico. 
    # Esto va fuera de process_street debido a que algunas fechas en la base tienen numero en digito y otros en alfanumerico
    
    
    ### --------------------------------------------------------------------------
    
    for loc in possible_locs:
        result = search_from_API(street,loc,dep)
        if not 'error' in result.keys():
            return result
        
        else:
            if not error:
                error = ' '.join((error,result.get('error')))
            else:
                error = result.get('error')
            result = search_from_frame(street,loc,dep,df)
            
            if 'error' in result.keys():
                error = ' '.join((error,result.get('error')))
                return {'error':error}
            
    return result

def search_street(street,loc,dep,df):
    """Calls get_data_INE for data of a street. 
    If it fails it changes the street name to fix INE notation problems (mostly dates) and tries again. 
    """
    result = get_data_IDE(street,loc,dep,df)
    #print("RESULT DE SEARCH STREET",result)
    special_streets = [("S/N","SIN NOMBRE"),("SN","SIN NOMBRE"),("CALLE","")] #Las calles especiales y sus correspondientes normalizaciones
    if 'error' in result.keys():
        for special in special_streets:
            if special[0] in street:
                street = street.replace(special[0],special[1])
                result = get_data_IDE(street,loc,dep,df)
                if 'error' not in result.keys():
                    break
    return result

def search_address(street,loc,dep,codificador,tryouts=3):
    """Finds a location """
    street = parse.unquote(street)
    street = street.upper().replace("S/N","1")
    
    street, number = process_street(street)
    
    #print("Entrada search address", street,number)
    
    validated_data = search_street(street,loc,dep,codificador)
    #print(validated_data)
    street = street + ' ' + number + ' '
    dep = dep.upper() + ' '
    loc = loc.upper()
    
    
    #street = result.get('calle') + str(result.get('numero')) +' ' # La api de direcciones exactas Quotea los caracteres especiales y agrega un espacio al final de cada valor
    #dep = result.get("departamento") + ' '
    #loc = result.get("localidad")
    root = 'https://direcciones.ide.uy/'
    URL = root + 'api/v0/geocode/BusquedaDireccion?'
    
    query_args = {
        "calle" : street, # La sugerencia a buscar
        "departamento":dep,
        "localidad":loc
    }
    
    while tryouts>0:
        try:
            r = request.urlopen(URL+parse.urlencode(query_args,quote_via=parse.quote))
            data = r.read().decode('utf-8').replace('null','None')
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
                     'error': e + ' en API IDE'})
                
                
    
    result = ast.literal_eval(data)
    #print(result)
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

        if street_id == validated_data.get('id'):
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
        
        #if 'PUNTO NO ENCONTRADO.' in result.get('error'):
        #    street += " 0" # Si falta numero de puerta hay que agregarselo por error en API IDE
        #    return search_address(street,loc,dep,codificador,tryouts=3)
    
        calle_nor = result.get('direccion').get('calle').get('nombre_normalizado')
        calle_id = result.get('direccion').get('calle').get('idCalle')
        nro_puerta = result.get('direccion').get('numero').get('nro_puerta')
        codigoPostal = result.get('codigoPostal')
        puntoX = result.get('puntoX')
        puntoY = result.get('puntoY')
        idPuntoIDE = result.get('idPunto')
        error = ""

        return ({'calleNormalizada':calle_nor,
                 'idCalleIDE':calle_id,
                 'nro_puerta_aprox':nro_puerta,
                 'codigoPostal':codigoPostal,
                 'puntoX':puntoX,
                 'puntoY':puntoY,
                 'idPuntoIDE':idPuntoIDE,
                 'error':error})
    
    elif street.split()[0].isdigit(): #Evita las calles '3'            
            # Algunas calles tienen nomenclatura ambigua en cuanto a los digitos en la base INE, por lo que hay que chequear. 
        street = digit_to_alphanumerical(street) 
           
        return search_address(street,loc,dep,codificador)
    else:
        return ({'calleNormalizada':'',
                     'idCalleIDE':'',
                     'nro_puerta':'',
                     'codigoPostal':'',
                     'puntoX':'',
                     'puntoY':'',
                     'idPuntoIDE':'',
                     'error':'No se encuentra dirección ingresada'})
