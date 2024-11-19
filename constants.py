SERVER_HOST = "10.0.0.24"
SERVER_PORT = 65432
server_response = ""
client_status = ""
elapsed_time = 0
raw_string = ""
corrected_string = ""

resources = {
    "GOLD": "", 
    "ELIXIR": "", 
    "DARK": ""
}

resource_values = {
    "GOLD": [],
    "ELIXIR": [],
    "DARK": []
}

averages = {
    "GOLD": 0.0,
    "ELIXIR": 0.0,
    "DARK": 0.0,
}

deviations = {
    "GOLD": 0.0,
    "ELIXIR": 0.0,
    "DARK": 0.0
}

translation_table = str.maketrans({
    'O': '0', 'o': '0',
    'B': '8',
    'L': '1', 'l': '1',
    'S': '5', 's': '5', '$': '5',
    '(': '1', ')': '1'
})