import _cmd
request = {
    "schema": [ {"name": "id", "type": "integer", "required": True} ],
    "rows": [ {"id": 1} ]
}
print(_cmd.call(request))
