import argparse
import json

from aiohttp import web
from llm import MODEL, get_response, init_model


async def handle_get(request):
    return web.Response(text="GET not allowed", status=403, content_type="text/plain")


async def handle_post(request):
    # Check path
    if request.path != "/generate":
        return web.json_response(
            {
                "status": 400,
                "body": f"Wrong endpoint: {request.path}\nPlease POST to /generate",
            },
            status=400,
        )

    # Check content type
    if request.content_type != "application/json":
        return web.json_response(
            {"status": 400, "body": "Unsupported content type"}, status=400
        )

    try:
        # Process JSON data
        data = await request.json()
        llm_response = get_response(
            request.app["model"], request.app["tokenizer"], data
        )

        return web.json_response({"status": 200, "body": str(llm_response)})

    except json.JSONDecodeError:
        return web.json_response(
            {"status": 400, "body": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        return web.json_response(
            {"status": 500, "body": f"Error processing request: {str(e)}"}, status=500
        )


def run_server(port):
    tokenizer, model = init_model(MODEL)

    app = web.Application()
    app["model"] = model
    app["tokenizer"] = tokenizer

    # Configure routes
    app.router.add_get("/{path:.*}", handle_get)
    app.router.add_post("/{path:.*}", handle_post)

    web.run_app(app, host="localhost", port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("prism-llm-server")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        required=True,
        help="Specify the port that the server will run on.",
    )
    args = parser.parse_args()
    run_server(args.port)
