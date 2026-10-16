FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

# Generate the word list text files at build time so startup only has to load
# them. The runtime fallback in app/dictionary.py still regenerates them if
# missing (e.g. when running locally without Docker).
RUN python -m scripts.generate_words

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
