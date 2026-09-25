TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set the Windows system volume.",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Volume level from 0 to 100."
                    }
                },
                "required": ["level"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_system_stats",
            "description": "Get CPU, RAM and disk usage of the computer.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open a Windows application.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application": {
                        "type": "string",
                        "description": "Name of the application to open."
                    }
                },
                "required": ["application"]
            }
        }
    }
]