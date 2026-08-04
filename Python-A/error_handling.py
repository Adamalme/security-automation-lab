{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Pineapple",
  "type": "object",
  "properties": {
    "name": {"type": "<string>"},
    "colors": {"type": "<array>"},
    "weight": {"type": "<number>"},
    "dimensions": {
      "type": "object",
      "properties": {
        "height": {"type": "<number>"},
        "diameter": {"type": "<number>"}
      }
    },
    "seedCount": {"type": "<number>"},
    "origin": {"type": "<string>"}
  }
}