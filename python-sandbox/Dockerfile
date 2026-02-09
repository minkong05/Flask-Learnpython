FROM python:3.10-slim

WORKDIR /sandbox

RUN useradd -ms /bin/bash sandbox_user
USER sandbox_user

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt

CMD sh -c "python app.py && docker run sandbox-image"