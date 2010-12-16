FILE_TYPE_TRANSLATOR = {"txt": "TEXT",
                        "int": "INTEGER",
                        "bin": "BLOB",
                        "nil": ""}

DB_TYPE_TRANSLATOR = {}
for key in FILE_TYPE_TRANSLATOR.keys():
    DB_TYPE_TRANSLATOR[FILE_TYPE_TRANSLATOR[key]] = key
        
FILE_SPECIAL_CASES = {"start":     "html",
                      "page":      "html",
                      "style":     "css",
                      "functions":  "js"}
