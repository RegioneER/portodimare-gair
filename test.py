import csv
import json
import re
"""
csvFilePath = "tools_r/static/script_r/1.11/pairwise_matrix.csv"

fieldnames = ("bathymetry", "coast_dist", "legislation", "trawl_fleet", "seine_fleet", "marine_traffic", "chlorophyl")
pairwise_matrix = {}
with open(csvFilePath, 'r') as csvfile:
    x=0
    for row in csvfile:
        if x > 0:
            list_row = row.split(',')
            name_row = list_row[0] 
            del list_row[0] 
            y = 0
            json_temp={}
            for value in list_row:
                json_temp[fieldnames[y]] = value
                y=y+1
            pairwise_matrix[name_row] = json_temp
                    
        x=x+1
    
print json.dumps(pairwise_matrix)
"""
"""
fieldnames = ("bathymetry", "coast_dist", "legislation", "trawl_fleet", "seine_fleet", "marine_traffic", "chlorophyl")
pairwise_matrix_str = '{"bathymetry":{"bathymetry":"1","coast_dist":"7","legislation":"7","trawl_fleet":"7","seine_fleet":"4","marine_traffic":"4","chlorophyl":"3"},"coast_dist":{"bathymetry":"0.14","coast_dist":"1","legislation":"6","trawl_fleet":"4","seine_fleet":"4","marine_traffic":"5","chlorophyl":"5"},"legislation":{"bathymetry":"0.14","coast_dist":"0.1666666667","legislation":"1","trawl_fleet":"1","seine_fleet":"2","marine_traffic":"1","chlorophyl":"0.5"},"trawl_fleet":{"bathymetry":"0.14","coast_dist":"0.25","legislation":"1","trawl_fleet":"1","seine_fleet":"3","marine_traffic":"3","chlorophyl":"0.5"},"seine_fleet":{"bathymetry":"0.25","coast_dist":"0.25","legislation":"0.5","trawl_fleet":"0.3333333333","seine_fleet":"1","marine_traffic":"2","chlorophyl":"0.3333333333"},"marine_traffic":{"bathymetry":"0.25","coast_dist":"0.2","legislation":"1","trawl_fleet":"0.3333333333","seine_fleet":"0.5","marine_traffic":"1","chlorophyl":"1"},"chlorophyl":{"bathymetry":"0.3333333333","coast_dist":"0.2","legislation":"2","trawl_fleet":"2","seine_fleet":"3","marine_traffic":"1","chlorophyl":"1"}}'
pairwise_matrix = json.loads(pairwise_matrix_str)

pairwise_matrix_csv = ','+','.join(map(str, fieldnames))+"\n"

for row in fieldnames:
    row_str = ""
    row_str += row
    for col in fieldnames:
        row_str += ','+pairwise_matrix[row][col]
    pairwise_matrix_csv += row_str+"\n"
   
f = open('pairwise_matrix.csv','w')
f.write(pairwise_matrix_csv) #Give your csv text here.
f.close()

#print json.dumps(pairwise_matrix)
"""
"""
nameField = ("Longitude", "Latitude", "GT")
fishing_gear = {}
with open("tools_r/static/script_r/1.11/Fishing_Gear.csv", 'r') as csvfile:
    x=0
    for row in csvfile:
        if x > 0:
            list_row = row.split(',')
            y = 0
            json_temp={}
            for value in list_row:
                json_temp[nameField[y]] = value.replace("\r\n","")
                y=y+1
                fishing_gear[x-1] = json_temp
        x=x+1

fishing_gear_json = json.dumps(fishing_gear)

fishing_gear = json.loads(fishing_gear_json)

fishing_gear_csv = ','.join(map(str, nameField))+"\n"
for elem in fishing_gear:
    row_obj = fishing_gear[elem]
    row_str = ""
    i=0
    for value in nameField:
        print value
        if i > 0:
            row_str += ','+row_obj[value]
        else:
            row_str += row_obj[value]
        i=i+1
    fishing_gear_csv += row_str+"\n"

print fishing_gear_csv
"""
"""
for row in fieldnames:
    row_str = ""
    row_str += row
    for col in fieldnames:
        row_str += ','+pairwise_matrix[row][col]
    pairwise_matrix_csv += row_str+"\n"
        
f = open(dir_output+'pairwise_matrix.csv','w')
f.write(pairwise_matrix_csv) #Give your csv text here.
f.close()
"""
"""
import re, string

def getNumbers(str): 
    array = re.findall(r"[-+]?\d*\.\d+|\d+", str) 
    return array 

def getAttribute(str): 
    array = re.split('\++|/+|-+|\*+|\(+|\)',str)
    return list(filter(lambda a: a != "", array)) 

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    

#expression = '(103+102+99)/\'2.0\''.replace("'", "")
expression = '(\'86#Area\'+82-86#Area+21*86)/\'100.0\''.replace("'", "")
print expression
list_numbers = getNumbers(expression) 
print "getNumbers"
print list_numbers
list_attributes = getAttribute(expression) 
print list_attributes
if "#" in list_attributes[0]:
    print "ciao"
for att in list_attributes: 
    if "#" in att:
        print att.split("#")[1]
alph = list(string.ascii_uppercase)


replacements = {}
i = 0
for num in list_numbers: 
    if RepresentsInt(num):
        replacements[num] = alph[i]
        i+=1

print replacements

#replacements[m.group()]
#converted_expression = re.sub(r"[-+]?\d*\.\d+|\d+", lambda m: RepresentsInt(m.group())?replacements[m.group()]:m.group(), expression)

#f = lambda m: str(int(m.group()))

#converted_expression = re.sub('^[-+]?[0-9]+$', f, expression)

def replTxt(match):
    return replacements[match.group()] if RepresentsInt(match.group()) else match.group()

i=0
expr_temp = expression
for attr in list_attributes:
    expr_temp = expr_temp.replace(attr,list_numbers[i])
    i=i+1
print expr_temp
a = re.compile(r"[-+]?\d*\.\d+|\d+")  
converted_expression = a.sub(replTxt, expr_temp)

print converted_expression
"""
"""
pairwise_matrix = {}
with open("/mnt/volumes/statics/static/script_r/1.11/pairwise_matrix.csv", 'r') as csvfile:
    fieldnames = ("bathymetry", "coast_dist", "legislation", "trawl_fleet", "seine_fleet", "marine_traffic", "chlorophyl")
    x=0
    for row in csvfile:
        if x > 0:
            list_row = row.split(',')
            name_row = list_row[0] 
            del list_row[0] 
            y = 0
            json_temp={}
            for value in list_row:
                json_temp[fieldnames[y]] = value
                y=y+1
                pairwise_matrix[name_row] = json_temp
                        
        x=x+1

print json.dumps(pairwise_matrix)
"""
"""
def getNumbers(str): 
    array = re.findall(r"\d*\.\d+|\d+", str) 
    return array 

str = getNumbers("1+10.3")

print str

"""
s = 'success, name folder documents -> [jfdvui]'
result = re.search('\[(.*)\]', s)
if (result):
    print(result.group(1))