import os

import uvicorn

if __name__ == '__main__':
    port: int = int(os.environ.get('SERVER_PORT', '8080'))
    host: str = os.environ.get('SERVER_HOST', '0.0.0.0')

    uvicorn.run("main:fastapi_app", host=host, port=port, reload=False, workers=1, log_config='logging.yaml')
