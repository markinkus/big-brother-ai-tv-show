import uvicorn


def main() -> None:
    uvicorn.run("neural_house_api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
